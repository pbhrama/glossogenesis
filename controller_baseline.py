import json
import os
from dataclasses import dataclass, field


@dataclass
class RoundLog:
    round_num: int
    speaker: str
    message: str
    proposal: dict
    agree: bool


@dataclass
class NegotiationResult:
    converged: bool
    rounds_used: int
    log: list = field(default_factory=list)


class BaselineController:
    """
    Runs the baseline two-agent negotiation: both agents share the full structured
    schema from round 1, no coined vocabulary, no sealed terms, no clarification cost.
    This is the comparison arm for the pidgin-protocol condition in controller.py.
    """

    def __init__(self, agent_a, agent_b, task: str,
                 token_budget: int = 40, max_rounds: int = 20, log_path: str | None = None):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.task = task
        self.token_budget = token_budget
        self.max_rounds = max_rounds
        self.log_path = log_path

    def run(self) -> NegotiationResult:
        speakers = [(self.agent_a, self.agent_b), (self.agent_b, self.agent_a)]
        incoming = None
        converged = False
        log = []

        for round_num in range(1, self.max_rounds + 1):
            speaker, listener = speakers[(round_num - 1) % 2]

            output = speaker.send(self.token_budget, self.task, incoming)
            message = output["message"]
            proposal = output.get("proposal", {})
            agree = bool(output.get("agree", False))

            entry = RoundLog(
                round_num=round_num,
                speaker=speaker.name,
                message=message,
                proposal=proposal,
                agree=agree,
            )
            log.append(entry)
            self._append_log(entry)

            incoming = message

            if agree and round_num > 1 and log[-2].agree:
                converged = True
                break

        return NegotiationResult(converged=converged, rounds_used=len(log), log=log)

    def _append_log(self, entry: RoundLog) -> None:
        if not self.log_path:
            return
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps({
                "round": entry.round_num,
                "speaker": entry.speaker,
                "message": entry.message,
                "proposal": entry.proposal,
                "agree": entry.agree,
            }) + "\n")
