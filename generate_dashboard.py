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


def main():
    summary = json.loads(SUMMARY_PATH.read_text())
    dictionary = json.loads(DICTIONARY_PATH.read_text())
    template = TEMPLATE_PATH.read_text()

    clarifications = [t["pidgin_clarification_rounds"] for t in summary]
    saved = clarifications[0] - clarifications[-1] if clarifications else 0

    payload = {
        "tasks": summary,
        "dictionary": list(dictionary.values()),
        "headline": {
            "first": clarifications[0] if clarifications else 0,
            "last": clarifications[-1] if clarifications else 0,
            "saved": saved,
        },
    }

    html = template.replace("__DASHBOARD_DATA__", json.dumps(payload, indent=2))
    OUT_PATH.write_text(html)
    print(f"Wrote {OUT_PATH} ({len(summary)} tasks, {len(dictionary)} dictionary terms)")


if __name__ == "__main__":
    main()
