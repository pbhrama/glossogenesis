import argparse
import json
import sys

from agents.base import make_procurement_agent, make_compliance_agent
from dictionary.store import DictionaryStore
from controller import TurnController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="tasks/task_01_vendor_onboarding.json")
    parser.add_argument("--dictionary", default="dictionary/shared_dictionary.json")
    parser.add_argument("--log", default="logs/task_01_run.jsonl")
    parser.add_argument("--budget", type=int, default=40)
    parser.add_argument("--max-rounds", type=int, default=16)
    args = parser.parse_args()

    with open(args.task) as f:
        task = json.load(f)

    dictionary = DictionaryStore.load(args.dictionary)
    agent_a = make_procurement_agent()
    agent_b = make_compliance_agent()

    controller = TurnController(
        agent_a=agent_a,
        agent_b=agent_b,
        task=task["description"],
        dictionary=dictionary,
        token_budget=args.budget,
        max_rounds=args.max_rounds,
        log_path=args.log,
    )

    result = controller.run()

    print(f"\nConverged: {result.converged}")
    print(f"Rounds used: {result.rounds_used}")
    print(f"Clarification rounds: {result.clarification_rounds}")
    print(f"Dictionary size: {result.final_dictionary_size}")
    print("\n--- Transcript ---")
    for entry in result.log:
        tag = " [COINED: " + ", ".join(entry.coined_terms) + "]" if entry.coined_terms else ""
        print(f"[{entry.round_num}] {entry.speaker}{tag}: {entry.message}")


if __name__ == "__main__":
    sys.exit(main())
