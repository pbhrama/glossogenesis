import argparse
import glob
import json
import os
import sys

from agents.base import make_procurement_agent as make_pidgin_procurement
from agents.base import make_compliance_agent as make_pidgin_compliance
from agents.base_baseline import make_procurement_agent as make_baseline_procurement
from agents.base_baseline import make_compliance_agent as make_baseline_compliance
from controller import TurnController
from controller_baseline import BaselineController
from dictionary.store import DictionaryStore


def run_pidgin(task, dictionary, budget, max_rounds, log_path):
    controller = TurnController(
        agent_a=make_pidgin_procurement(),
        agent_b=make_pidgin_compliance(),
        task=task["description"],
        dictionary=dictionary,
        token_budget=budget,
        max_rounds=max_rounds,
        log_path=log_path,
    )
    result = controller.run()
    return {
        "converged": result.converged,
        "rounds_used": result.rounds_used,
        "clarification_rounds": result.clarification_rounds,
        "dictionary_size_after": result.final_dictionary_size,
    }


def run_baseline(task, budget, max_rounds, log_path):
    controller = BaselineController(
        agent_a=make_baseline_procurement(),
        agent_b=make_baseline_compliance(),
        task=task["description"],
        token_budget=budget,
        max_rounds=max_rounds,
        log_path=log_path,
    )
    result = controller.run()
    return {
        "converged": result.converged,
        "rounds_used": result.rounds_used,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", default="tasks")
    parser.add_argument("--dictionary", default="dictionary/shared_dictionary.json")
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--budget", type=int, default=40)
    parser.add_argument("--max-rounds", type=int, default=16)
    parser.add_argument("--reset-dictionary", action="store_true",
                         help="start the pidgin dictionary empty instead of loading existing state")
    parser.add_argument("--summary-out", default="logs/summary.json")
    args = parser.parse_args()

    task_paths = sorted(glob.glob(os.path.join(args.tasks_dir, "*.json")))
    if not task_paths:
        print(f"No task files found in {args.tasks_dir}", file=sys.stderr)
        return 1

    if args.reset_dictionary and os.path.exists(args.dictionary):
        os.remove(args.dictionary)
    dictionary = DictionaryStore.load(args.dictionary)

    summary = []
    for task_path in task_paths:
        with open(task_path) as f:
            task = json.load(f)
        task_id = task["id"]
        print(f"\n=== {task_id} ===")

        pidgin_log = os.path.join(args.log_dir, f"{task_id}_pidgin.jsonl")
        baseline_log = os.path.join(args.log_dir, f"{task_id}_baseline.jsonl")
        for stale in (pidgin_log, baseline_log):
            if os.path.exists(stale):
                os.remove(stale)

        dict_size_before = len(dictionary.terms)
        pidgin = run_pidgin(task, dictionary, args.budget, args.max_rounds, pidgin_log)
        baseline = run_baseline(task, args.budget, args.max_rounds, baseline_log)

        row = {
            "task_id": task_id,
            "dictionary_size_before": dict_size_before,
            "pidgin_rounds": pidgin["rounds_used"],
            "pidgin_converged": pidgin["converged"],
            "pidgin_clarification_rounds": pidgin["clarification_rounds"],
            "baseline_rounds": baseline["rounds_used"],
            "baseline_converged": baseline["converged"],
        }
        summary.append(row)
        print(f"  pidgin:   {pidgin['rounds_used']} rounds, "
              f"{pidgin['clarification_rounds']} clarification, "
              f"converged={pidgin['converged']}, dict size now {pidgin['dictionary_size_after']}")
        print(f"  baseline: {baseline['rounds_used']} rounds, converged={baseline['converged']}")

    os.makedirs(os.path.dirname(args.summary_out) or ".", exist_ok=True)
    with open(args.summary_out, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n--- Learning curve (pidgin rounds vs. baseline rounds, in task order) ---")
    print(f"{'task':35} {'dict_before':>11} {'pidgin_rd':>9} {'clarif':>6} {'base_rd':>7}")
    for row in summary:
        print(f"{row['task_id']:35} {row['dictionary_size_before']:>11} "
              f"{row['pidgin_rounds']:>9} {row['pidgin_clarification_rounds']:>6} "
              f"{row['baseline_rounds']:>7}")
    print(f"\nSummary written to {args.summary_out}")


if __name__ == "__main__":
    sys.exit(main())
