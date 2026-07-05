"""Regenerates docs/dashboard.html from logs/summary.json and dictionary/shared_dictionary.json.

Run after run_all_tasks.py to refresh the dashboard with the latest results.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
SUMMARY_PATH = ROOT / "logs" / "summary.json"
DICTIONARY_PATH = ROOT / "dictionary" / "shared_dictionary.json"
OUT_PATH = ROOT / "docs" / "dashboard.html"
TEMPLATE_PATH = ROOT / "docs" / "dashboard_template.html"


def normalize(row):
    """Accept either the flat single-run schema or the averaged --reps schema and emit
    the flat keys the dashboard template reads (means, when averaged)."""
    if "pidgin_rounds_mean" in row:  # averaged (--reps) schema
        return {
            "task_id": row["task_id"],
            "pidgin_rounds": row["pidgin_rounds_mean"],
            "pidgin_clarification_rounds": row["pidgin_clarification_mean"],
            "baseline_rounds": row["baseline_rounds_mean"],
            "reps": row.get("reps", 1),
        }
    return {  # flat single-run schema
        "task_id": row["task_id"],
        "pidgin_rounds": row["pidgin_rounds"],
        "pidgin_clarification_rounds": row["pidgin_clarification_rounds"],
        "baseline_rounds": row["baseline_rounds"],
        "reps": 1,
    }


def main():
    summary = json.loads(SUMMARY_PATH.read_text())
    dictionary = json.loads(DICTIONARY_PATH.read_text())
    template = TEMPLATE_PATH.read_text()

    tasks = [normalize(t) for t in summary]
    clarifications = [t["pidgin_clarification_rounds"] for t in tasks]
    saved = clarifications[0] - clarifications[-1] if clarifications else 0
    reps = tasks[0]["reps"] if tasks else 1

    payload = {
        "tasks": tasks,
        "dictionary": list(dictionary.values()),
        "reps": reps,
        "headline": {
            "first": clarifications[0] if clarifications else 0,
            "last": clarifications[-1] if clarifications else 0,
            "saved": saved,
        },
    }

    html = template.replace("__DASHBOARD_DATA__", json.dumps(payload, indent=2))
    OUT_PATH.write_text(html)
    note = f", averaged over {reps} reps" if reps > 1 else ""
    print(f"Wrote {OUT_PATH} ({len(tasks)} tasks, {len(dictionary)} dictionary terms{note})")


if __name__ == "__main__":
    main()
