"""
Alibaba Cloud Function Compute entrypoint. Runs one pidgin-protocol negotiation and
returns the result as JSON. Deployed via s.yaml (see DEPLOY.md) -- config values below
come entirely from Function Compute environment variables set at deploy time, never
committed to this repo:

  DASHSCOPE_API_KEY   -- Qwen Cloud API key
  REDIS_HOST          -- ApsaraDB for Redis instance host
  REDIS_PORT          -- default 6379
  REDIS_PASSWORD      -- optional, if instance requires auth
  REDIS_DB            -- default 0

Invoke event body (JSON):
  {
    "task_id": "task_01_vendor_onboarding",   # loads tasks/<task_id>.json bundled in the package
    "budget": 40,                              # optional, default 40
    "max_rounds": 16                           # optional, default 16
  }
"""
import json
import os

from agents.base import make_procurement_agent, make_compliance_agent
from controller import TurnController
from dictionary.store_redis import RedisDictionaryStore


def _load_task(task_id: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "tasks", f"{task_id}.json")
    with open(path) as f:
        return json.load(f)


def handler(event, context):
    body = json.loads(event) if isinstance(event, (str, bytes)) else event
    task_id = body["task_id"]
    budget = int(body.get("budget", 40))
    max_rounds = int(body.get("max_rounds", 16))

    task = _load_task(task_id)
    dictionary = RedisDictionaryStore.from_env()

    controller = TurnController(
        agent_a=make_procurement_agent(),
        agent_b=make_compliance_agent(),
        task=task["description"],
        dictionary=dictionary,
        token_budget=budget,
        max_rounds=max_rounds,
        log_path=None,
    )
    result = controller.run()

    return {
        "task_id": task_id,
        "converged": result.converged,
        "rounds_used": result.rounds_used,
        "clarification_rounds": result.clarification_rounds,
        "dictionary_size_after": result.final_dictionary_size,
        "transcript": [
            {
                "round": entry.round_num,
                "speaker": entry.speaker,
                "message": entry.message,
                "coined_terms": entry.coined_terms,
                "agree": entry.agree,
            }
            for entry in result.log
        ],
    }
