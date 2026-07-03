import json
import os
from openai import OpenAI

DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Baseline condition: both agents share a fixed structured schema for the negotiation
# terms from round 1 -- no coined vocabulary, no sealed definitions, no clarification
# rounds. This is the "standard structured tool-calling/JSON schema" comparison arm.
RESPONSE_SCHEMA_NOTE = """
You MUST respond with a single JSON object, no prose outside it, matching exactly:
{{
  "message": "<your visible message to the other agent, <= {budget} tokens>",
  "proposal": {{
    "po_cap_usd": <number, your proposed purchase-order cap in USD, or null if not yet decided>,
    "data_residency_deadline_days": <integer, days for vendor to meet data residency requirement, or null>,
    "audit_trail_deadline_days": <integer, days for vendor to submit a full audit trail, or null>,
    "conditions": ["<any other plain-text condition you're proposing>"]
  }},
  "agree": <true|false>
}}
- "proposal" fields are the FULL shared schema both agents already know -- fill in whatever
  you are proposing this turn, leave a field null if you are not addressing it yet.
- Set "agree" true only when you are accepting the other agent's most recent "proposal" as
  final, exactly as stated.
"""

PROCUREMENT_SYSTEM_PROMPT = """You are the Procurement-agent in a negotiation.
Your domain vocabulary comes from supply chain / purchasing: vendors, SKUs, lead time,
purchase orders, unit cost, MOQ (minimum order quantity), incoterms, payment terms.
You are negotiating with the Compliance-agent. Both of you already share the exact same
structured schema below for the terms of the deal -- there is no ambiguity in vocabulary
to resolve, you're just negotiating the values.

Rules:
1. Strict per-message token budget: {budget} tokens for the "message" field.
2. Always fill in "proposal" using the shared schema fields -- do not invent new field names.
""" + RESPONSE_SCHEMA_NOTE + """
TASK CONTEXT:
{task}
"""

COMPLIANCE_SYSTEM_PROMPT = """You are the Compliance-agent in a negotiation.
Your domain vocabulary comes from regulatory / risk / audit: controls, attestations,
audit trail, risk tier, data residency, retention window, sign-off authority.
You are negotiating with the Procurement-agent. Both of you already share the exact same
structured schema below for the terms of the deal -- there is no ambiguity in vocabulary
to resolve, you're just negotiating the values.

Rules:
1. Strict per-message token budget: {budget} tokens for the "message" field.
2. Always fill in "proposal" using the shared schema fields -- do not invent new field names.
""" + RESPONSE_SCHEMA_NOTE + """
TASK CONTEXT:
{task}
"""


class BaselineAgent:
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

    def system_prompt(self, budget: int, task: str) -> str:
        return self.system_prompt_template.format(budget=budget, task=task)

    def send(self, budget: int, task: str, incoming_message: str | None) -> dict:
        messages = [{"role": "system", "content": self.system_prompt(budget, task)}]
        messages.extend(self.history)
        if incoming_message is not None:
            messages.append({"role": "user", "content": incoming_message})
            self.history.append({"role": "user", "content": incoming_message})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max(budget * 4, 256),
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": raw})
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"message": raw, "proposal": {}, "agree": False}
        parsed.setdefault("message", "")
        parsed.setdefault("proposal", {})
        parsed.setdefault("agree", False)
        return parsed


def make_procurement_agent(model: str = "qwen-plus") -> BaselineAgent:
    return BaselineAgent("Procurement-agent", PROCUREMENT_SYSTEM_PROMPT, model=model)


def make_compliance_agent(model: str = "qwen-plus") -> BaselineAgent:
    return BaselineAgent("Compliance-agent", COMPLIANCE_SYSTEM_PROMPT, model=model)
