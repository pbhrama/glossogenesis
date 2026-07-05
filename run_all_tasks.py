import argparse
import glob
import json
import os
import statistics
import sys

from agents.base import make_procurement_agent as make_pidgin_procurement
from agents.base import make_compliance_agent as make_pidgin_compliance
from agents.base_baseline import make_procurement_agent as make_baseline_procurement
from agents.base_baseline import make_compliance_agent as make_baseline_compliance
from controller import TurnController
from controller_baseline import BaselineController
from dictionary.store import DictionaryStore, Term


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


def clone_dictionary(dictionary, scratch_path):
    """
    A throwaway copy of the dictionary's current terms, written to a scratch path so
    reps beyond the first can coin/resolve terms without mutating the canonical
    dictionary or the reps racing each other on the same file.
    """
    terms_copy = {k: Term(**vars(v)) for k, v in dictionary.terms.items()}
    return DictionaryStore(path=scratch_path, terms=terms_copy)


def mean_sd(values):
    m = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return round(m, 2), round(sd, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", default="tasks")
    parser.add_argument("--dictionary", default="dictionary/shared_dictionary.json")
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--budget", type=int, default=40)
    parser.add_argument("--max-rounds", type=int, default=16)
    parser.add_argument("--reps", type=int, default=1,
                         help="repeat each task this many times per condition and average, to "
                              "smooth out round-count noise from how contentious a task's "
                              "content happens to be. Only rep 0 advances the canonical pidgin "
                              "dictionary that carries forward to later tasks; reps 1..N-1 run "
                              "against a scratch copy of that dictionary and are discarded.")
    parser.add_argument("--reset-dictionary", action="store_true",
                         help="start the pidgin dictionary empty instead of loading existing state")
    parser.add_argument("--summary-out", default="logs/summary.json")
    args = parser.parse_args()

    # Only the numbered experiment tasks (task_01..NN). The themed demo scenarios
    # (task_firstcontact / task_spacecraft) use their own personas and are NOT part of
    # the measured pidgin-vs-baseline learning-curve experiment, so they are excluded here.
    task_paths = sorted(glob.glob(os.path.join(args.tasks_dir, "task_[0-9]*.json")))
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

        dict_size_before = len(dictionary.terms)
        pidgin_rounds, pidgin_clarifications, pidgin_converged = [], [], []
        baseline_rounds, baseline_converged = [], []

        for rep in range(args.reps):
            pidgin_log = os.path.join(args.log_dir, f"{task_id}_pidgin_rep{rep}.jsonl")
            baseline_log = os.path.join(args.log_dir, f"{task_id}_baseline_rep{rep}.jsonl")
            for stale in (pidgin_log, baseline_log):
                if os.path.exists(stale):
                    os.remove(stale)

            if rep == 0:
                rep_dictionary = dictionary
            else:
                scratch_path = os.path.join(args.log_dir, f"{task_id}_pidgin_rep{rep}_scratch_dict.json")
                rep_dictionary = clone_dictionary(dictionary, scratch_path)

            pidgin = run_pidgin(task, rep_dictionary, args.budget, args.max_rounds, pidgin_log)
            baseline = run_baseline(task, args.budget, args.max_rounds, baseline_log)

            pidgin_rounds.append(pidgin["rounds_used"])
            pidgin_clarifications.append(pidgin["clarification_rounds"])
            pidgin_converged.append(pidgin["converged"])
            baseline_rounds.append(baseline["rounds_used"])
            baseline_converged.append(baseline["converged"])

            print(f"  [rep {rep}] pidgin: {pidgin['rounds_used']} rounds, "
                  f"{pidgin['clarification_rounds']} clarification, converged={pidgin['converged']} | "
                  f"baseline: {baseline['rounds_used']} rounds, converged={baseline['converged']}")

        pidgin_rounds_mean, pidgin_rounds_sd = mean_sd(pidgin_rounds)
        pidgin_clarif_mean, pidgin_clarif_sd = mean_sd(pidgin_clarifications)
        baseline_rounds_mean, baseline_rounds_sd = mean_sd(baseline_rounds)

        row = {
            "task_id": task_id,
            "reps": args.reps,
            "dictionary_size_before": dict_size_before,
            "dictionary_size_after_canonical": len(dictionary.terms),
            "pidgin_rounds_mean": pidgin_rounds_mean,
            "pidgin_rounds_sd": pidgin_rounds_sd,
            "pidgin_rounds_all": pidgin_rounds,
            "pidgin_clarification_mean": pidgin_clarif_mean,
            "pidgin_clarification_sd": pidgin_clarif_sd,
            "pidgin_clarification_all": pidgin_clarifications,
            "pidgin_converged_rate": sum(pidgin_converged) / len(pidgin_converged),
            "baseline_rounds_mean": baseline_rounds_mean,
            "baseline_rounds_sd": baseline_rounds_sd,
            "baseline_rounds_all": baseline_rounds,
            "baseline_converged_rate": sum(baseline_converged) / len(baseline_converged),
        }
        summary.append(row)
        print(f"  MEAN: pidgin {pidgin_rounds_mean}±{pidgin_rounds_sd} rounds, "
              f"{pidgin_clarif_mean}±{pidgin_clarif_sd} clarification | "
              f"baseline {baseline_rounds_mean}±{baseline_rounds_sd} rounds")

    os.makedirs(os.path.dirname(args.summary_out) or ".", exist_ok=True)
    with open(args.summary_out, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n--- Learning curve (mean rounds across reps, in task order) ---")
    print(f"{'task':35} {'dict_before':>11} {'pidgin_rd':>13} {'clarif':>13} {'base_rd':>13}")
    for row in summary:
        print(f"{row['task_id']:35} {row['dictionary_size_before']:>11} "
              f"{row['pidgin_rounds_mean']:>7}±{row['pidgin_rounds_sd']:<5} "
              f"{row['pidgin_clarification_mean']:>7}±{row['pidgin_clarification_sd']:<5} "
              f"{row['baseline_rounds_mean']:>7}±{row['baseline_rounds_sd']:<5}")
    print(f"\nSummary written to {args.summary_out}")


if __name__ == "__main__":
    sys.exit(main())
