import argparse
import json
import sys

from agents.base_baseline import make_procurement_agent, make_compliance_agent
from controller_baseline import BaselineController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="tasks/task_01_vendor_onboarding.json")
    parser.add_argument("--log", default="logs/task_01_baseline_run.jsonl")
    parser.add_argument("--budget", type=int, default=40)
    parser.add_argument("--max-rounds", type=int, default=16)
    args = parser.parse_args()

    with open(args.task) as f:
        task = json.load(f)

    agent_a = make_procurement_agent()
    agent_b = make_compliance_agent()

    controller = BaselineController(
        agent_a=agent_a,
        agent_b=agent_b,
        task=task["description"],
        token_budget=args.budget,
        max_rounds=args.max_rounds,
        log_path=args.log,
    )

    result = controller.run()

    print(f"\nConverged: {result.converged}")
    print(f"Rounds used: {result.rounds_used}")
    print("\n--- Transcript ---")
    for entry in result.log:
        print(f"[{entry.round_num}] {entry.speaker}: {entry.message}")
        if entry.proposal:
            print(f"    proposal: {entry.proposal}")


if __name__ == "__main__":
    sys.exit(main())
