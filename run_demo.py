"""Scenario-aware demo runner.

Runs a single negotiation for one of the themed scenarios (first-contact,
spacecraft) or the original vendor scenario. Same TurnController and sealed-term
mechanic as run_negotiation.py -- only the agent personas and task change.

Usage:
    python run_demo.py --scenario firstcontact
    python run_demo.py --scenario spacecraft --budget 45 --max-rounds 24
"""
import argparse
import json
import sys

from dictionary.store import DictionaryStore
from controller import TurnController

from agents.base import make_procurement_agent, make_compliance_agent
from agents.base_medical import make_physician_agent, make_insurer_agent
from agents.base_startup import make_founder_agent, make_investor_agent
from agents.base_security import make_engineer_agent, make_security_agent


SCENARIOS = {
    "medical": {
        "task": "tasks/task_medical.json",
        "agent_a": make_physician_agent,
        "agent_b": make_insurer_agent,
    },
    "startup": {
        "task": "tasks/task_startup.json",
        "agent_a": make_founder_agent,
        "agent_b": make_investor_agent,
    },
    "security": {
        "task": "tasks/task_security.json",
        "agent_a": make_engineer_agent,
        "agent_b": make_security_agent,
    },
    "vendor": {
        "task": "tasks/task_01_vendor_onboarding.json",
        "agent_a": make_procurement_agent,
        "agent_b": make_compliance_agent,
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=SCENARIOS.keys(), default="medical")
    parser.add_argument("--task", default=None, help="override the scenario's default task file")
    parser.add_argument("--dictionary", default=None,
                        help="dictionary file to load/seed (default: a fresh empty one per scenario)")
    parser.add_argument("--log", default=None)
    parser.add_argument("--budget", type=int, default=45)
    parser.add_argument("--max-rounds", type=int, default=24)
    args = parser.parse_args()

    scenario = SCENARIOS[args.scenario]
    task_path = args.task or scenario["task"]
    log_path = args.log or f"logs/demo_{args.scenario}.jsonl"

    with open(task_path) as f:
        task = json.load(f)

    if args.dictionary:
        dictionary = DictionaryStore.load(args.dictionary)
    else:
        # fresh, in-memory-only dictionary so each demo starts from zero shared words
        dictionary = DictionaryStore(path=None)

    agent_a = scenario["agent_a"]()
    agent_b = scenario["agent_b"]()

    controller = TurnController(
        agent_a=agent_a,
        agent_b=agent_b,
        task=task["description"],
        dictionary=dictionary,
        token_budget=args.budget,
        max_rounds=args.max_rounds,
        log_path=log_path,
    )

    print(f"\n--- {args.scenario} negotiation (live) ---\n")
    result = controller.run(verbose=True)

    print(f"\n--- Result ---")
    print(f"Converged: {result.converged}")
    print(f"Rounds used: {result.rounds_used}")
    print(f"Clarification rounds: {result.clarification_rounds}")
    print(f"Shared terms built: {result.final_dictionary_size}")


if __name__ == "__main__":
    sys.exit(main())
