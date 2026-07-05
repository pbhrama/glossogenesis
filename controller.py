import json
import os
from dataclasses import dataclass, field

from dictionary.store import DictionaryStore


@dataclass
class RoundLog:
    round_num: int
    speaker: str
    message: str
    coined_terms: list
    forced_clarification: bool
    agree: bool


@dataclass
class NegotiationResult:
    converged: bool
    rounds_used: int
    clarification_rounds: int
    final_dictionary_size: int
    log: list = field(default_factory=list)


class TurnController:
    """
    Runs a two-agent negotiation over a task.

    Enforcement is deterministic, not left to instruction-following:
    - Each agent's visible "message" is capped by token budget (enforced via max_tokens
      at the API layer; we also just trust the model to stay under the field budget since
      it's asked to).
    - A coined term is SEALED: its definition is withheld from the other agent's view of
      the transcript until a clarification round has been spent. This is what gives the
      "extra round" cost real teeth -- the other agent literally cannot see the definition
      early, regardless of what either model decides to do.
    - Agreement only counts once both agents have agreed with no pending sealed terms.
    """

    def __init__(self, agent_a, agent_b, task: str, dictionary: DictionaryStore,
                 token_budget: int = 40, max_rounds: int = 20, log_path: str | None = None):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.task = task
        self.dictionary = dictionary
        self.token_budget = token_budget
        self.max_rounds = max_rounds
        self.log_path = log_path
        self.sealed_terms: dict[str, dict] = {}  # term -> {definition, coined_by}

    def _visible_message(self, message: str) -> str:
        # Strip nothing -- the message text itself is always visible. Only the
        # *definitions* of newly coined terms are sealed until asked about.
        return message

    def _pending_terms_note(self, speaker_history_has_pending: bool) -> str:
        if not self.sealed_terms:
            return ""
        pending = ", ".join(f'"{t}"' for t in self.sealed_terms)
        return (f"\n\n[SYSTEM NOTE: the terms {pending} have been used but not yet defined "
                f"for you. If you need to know what one means, put it in your \"asking_about\" "
                f"list this turn -- you'll get the real definition next turn. This costs a "
                f"round, so only ask if you actually need it; do not guess at the meaning and "
                f"use the term as if you already knew it.]")

    def run(self, verbose: bool = False) -> NegotiationResult:
        speakers = [(self.agent_a, self.agent_b), (self.agent_b, self.agent_a)]
        incoming = None
        clarification_rounds = 0
        converged = False
        log = []

        for round_num in range(1, self.max_rounds + 1):
            speaker, listener = speakers[(round_num - 1) % 2]

            if verbose:
                # distinct color per speaker so it reads as a two-sided dialogue
                name_color = "\033[94m" if speaker is self.agent_a else "\033[92m"
                print(f"\n{name_color}{speaker.name}\033[0m is thinking...", end="", flush=True)

            dict_block = self.dictionary.as_prompt_block()
            msg_to_send = incoming
            if incoming is not None:
                msg_to_send = incoming + self._pending_terms_note(True)

            output = speaker.send(self.token_budget, dict_block, self.task, msg_to_send)
            message = output["message"]
            new_terms = output.get("new_terms", [])
            asking_about = output.get("asking_about", [])
            agree = bool(output.get("agree", False))

            forced_clarification = False
            newly_coined = set()
            for nt in new_terms:
                term = nt.get("term", "").strip()
                definition = nt.get("definition", "").strip()
                if not term or self.dictionary.has(term):
                    continue
                if term in self.sealed_terms:
                    continue
                self.sealed_terms[term] = {"definition": definition, "coined_by": speaker.name}
                newly_coined.add(term)
                forced_clarification = True

            # Only an EXPLICIT request via "asking_about" reveals a sealed term -- this is what
            # gives the "extra round" cost real teeth. A term merely reappearing in conversation
            # text (e.g. because the coiner used it in their own message) must NOT auto-resolve
            # it; a speaker also can't resolve a term they just coined this same turn.
            for term in asking_about:
                term = term.strip()
                if term not in self.sealed_terms or term in newly_coined:
                    continue
                entry = self.sealed_terms.pop(term)
                self.dictionary.add(term, entry["definition"], entry["coined_by"], round_num)
                clarification_rounds += 1

            entry = RoundLog(
                round_num=round_num,
                speaker=speaker.name,
                message=message,
                coined_terms=[nt.get("term") for nt in new_terms],
                forced_clarification=forced_clarification,
                agree=agree,
            )
            log.append(entry)
            self._append_log(entry)

            if verbose:
                coined = entry.coined_terms
                asked = [t.strip() for t in asking_about if t.strip()]
                tag = ""
                if coined:
                    tag += "  \033[35m[coins: " + ", ".join(c for c in coined if c) + "]\033[0m"
                if asked:
                    tag += "  \033[36m[asks: " + ", ".join(asked) + "]\033[0m"
                # \r + \033[K clears the "is thinking..." line, then print the finished round
                name_color = "\033[94m" if speaker is self.agent_a else "\033[92m"
                rnd = f"\033[2m{round_num:>2}\033[0m"  # dim round number
                print(f"\r\033[K{rnd}  {name_color}\033[1m{speaker.name}\033[0m: {message}{tag}")

            incoming = message

            if agree and round_num > 1 and log[-2].agree and not self.sealed_terms:
                converged = True
                break

        result = NegotiationResult(
            converged=converged,
            rounds_used=len(log),
            clarification_rounds=clarification_rounds,
            final_dictionary_size=len(self.dictionary.terms),
            log=log,
        )
        return result

    def _append_log(self, entry: RoundLog) -> None:
        if not self.log_path:
            return
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps({
                "round": entry.round_num,
                "speaker": entry.speaker,
                "message": entry.message,
                "coined_terms": entry.coined_terms,
                "forced_clarification": entry.forced_clarification,
                "agree": entry.agree,
            }) + "\n")
