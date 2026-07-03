import json
import os
from openai import OpenAI

DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

RESPONSE_SCHEMA_NOTE = """
You MUST respond with a single JSON object, no prose outside it, matching exactly:
{{
  "message": "<your visible message to the other agent, <= {budget} tokens>",
  "new_terms": [{{"term": "<short coined term>", "definition": "<what it means, kept SEALED>"}}],
  "asking_about": ["<sealed term you are explicitly requesting the definition of, if any>"],
  "agree": <true|false>
}}
- "new_terms" lists any NEW compressed terms you use in "message" that are not yet in the
  shared dictionary. Do NOT put the definition inside "message" itself -- the definition
  only becomes visible to the other agent if they explicitly ask what the term means in a
  later round. This is what makes coining a term costly: the other agent must spend a round
  asking before they can use it.
- If "message" only uses terms already in the shared dictionary (or plain language), leave
  "new_terms" empty.
- "asking_about" is how you REQUEST a definition for a sealed term you don't know yet -- list
  it there (and say so in "message", e.g. "what does X mean?") and you'll receive the real
  definition on your NEXT turn. Do not guess at a sealed term's meaning and use it as if you
  already knew it -- that defeats the negotiation's constraint. Leave "asking_about" empty if
  you are not requesting any definition this turn.
- Set "agree" true only when you are accepting the current proposal as final.
"""

PROCUREMENT_SYSTEM_PROMPT = """You are the Procurement-agent in a negotiation.
Your domain vocabulary comes from supply chain / purchasing: vendors, SKUs, lead time,
purchase orders, unit cost, MOQ (minimum order quantity), incoterms, payment terms.
You are negotiating with the Compliance-agent, who does NOT share your vocabulary and
uses different terms for overlapping concepts.

Rules:
1. Strict per-message token budget: {budget} tokens for the "message" field.
2. Reuse any term already in the SHARED DICTIONARY below with its agreed meaning -- this is
   free and encouraged, it's how you stay under budget.
3. You may coin a NEW term instead of spelling things out, but an unresolved new term costs
   the other agent an extra round to ask what it means before real progress continues.
4. Do not invent a shared schema or reveal a full glossary up front. Vocabulary must emerge
   turn by turn, from necessity.
""" + RESPONSE_SCHEMA_NOTE + """
SHARED DICTIONARY (terms already agreed with the other agent):
{dictionary}

TASK CONTEXT:
{task}
"""

COMPLIANCE_SYSTEM_PROMPT = """You are the Compliance-agent in a negotiation.
Your domain vocabulary comes from regulatory / risk / audit: controls, attestations,
audit trail, risk tier, data residency, retention window, sign-off authority.
You are negotiating with the Procurement-agent, who does NOT share your vocabulary and
uses different terms for overlapping concepts.

Rules:
1. Strict per-message token budget: {budget} tokens for the "message" field.
2. Reuse any term already in the SHARED DICTIONARY below with its agreed meaning -- this is
   free and encouraged, it's how you stay under budget.
3. You may coin a NEW term instead of spelling things out, but an unresolved new term costs
   the other agent an extra round to ask what it means before real progress continues.
4. Do not invent a shared schema or reveal a full glossary up front. Vocabulary must emerge
   turn by turn, from necessity.
""" + RESPONSE_SCHEMA_NOTE + """
SHARED DICTIONARY (terms already agreed with the other agent):
{dictionary}

TASK CONTEXT:
{task}
"""


class QwenAgent:
    def __init__(self, name: str, system_prompt_template: str, model: str | None = None):
        model = model or os.environ.get("QWEN_MODEL", "qwen-plus")
        self.name = name
        self.system_prompt_template = system_prompt_template
        self.model = model
        self.client = OpenAI(
            api_key=os.environ["DASHSCOPE_API_KEY"],
            base_url=DASHSCOPE_BASE_URL,
        )
        self.history = []

    def system_prompt(self, budget: int, dictionary_block: str, task: str) -> str:
        return self.system_prompt_template.format(
            budget=budget, dictionary=dictionary_block, task=task
        )

    def send(self, budget: int, dictionary_block: str, task: str, incoming_message: str | None) -> dict:
        messages = [{"role": "system", "content": self.system_prompt(budget, dictionary_block, task)}]
        messages.extend(self.history)
        if incoming_message is not None:
            messages.append({"role": "user", "content": incoming_message})
            self.history.append({"role": "user", "content": incoming_message})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max(budget * 4, 256),  # headroom for JSON wrapper + sealed definitions
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": raw})
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"message": raw, "new_terms": [], "asking_about": [], "agree": False}
        parsed.setdefault("message", "")
        parsed.setdefault("new_terms", [])
        parsed.setdefault("asking_about", [])
        parsed.setdefault("agree", False)
        return parsed


def make_procurement_agent(model: str = "qwen-plus") -> QwenAgent:
    return QwenAgent("Procurement-agent", PROCUREMENT_SYSTEM_PROMPT, model=model)


def make_compliance_agent(model: str = "qwen-plus") -> QwenAgent:
    return QwenAgent("Compliance-agent", COMPLIANCE_SYSTEM_PROMPT, model=model)
