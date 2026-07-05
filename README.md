# Glossogenesis

Multi-agent negotiation system built for the Global AI Hackathon w/ Qwen Cloud (Track 3: Agent Society).

Two Qwen-powered agents with distinct domain vocabularies — a Procurement-agent and a
Compliance-agent — negotiate a task under a strict token/message budget with **no shared schema
upfront**. That constraint forces them to build a compressed "pidgin" dictionary of shared terms
over the course of a negotiation, which we compare against a baseline where the agents are given
a full structured schema from the start.

## Architecture

![Architecture diagram](docs/architecture.svg)

- **Pidgin condition**: `agents/base.py` + `controller.py` (`TurnController`), backed by a shared
  `DictionaryStore` (`dictionary/store.py`, or `dictionary/store_redis.py` for the cloud-deployed
  variant). A coined term costs the other agent an extra round to ask "what does X mean?" before
  it's usable freely.
- **Baseline condition**: `agents/base_baseline.py` + `controller_baseline.py`
  (`BaselineController`) — same personas, full shared JSON schema known upfront, no coined
  vocabulary, no sealing.
- Both conditions call the same Qwen Cloud API (`qwen-plus`, OpenAI-compatible SDK,
  `dashscope-intl` endpoint) so any convergence-speed difference is driven by the
  schema/vocabulary constraint, not a model capability gap.
- `run_all_tasks.py` runs both arms across a batch of tasks (`tasks/task_01..05.json`), carrying
  the pidgin dictionary forward between tasks, and writes `logs/summary.json`.

## Core result

Across 5 tasks, the pidgin arm's **clarification cost drops to 0 after task_01** and stays there —
the 3-term dictionary built while negotiating the first task gets reused for free on every task
after. Raw round count doesn't cleanly decrease (task content difficulty varies independently of
vocabulary cost), so the clean metric is clarification-rounds-saved, not raw round count.

Run `python generate_dashboard.py` to regenerate [`docs/dashboard.html`](docs/dashboard.html) — a
self-contained dashboard (convergence charts, the learning curve, and the live shared dictionary)
built from `logs/summary.json` and `dictionary/shared_dictionary.json`.

## Try it — demo scenarios

`run_demo.py` runs a single live negotiation and streams each round as it happens (coined words and
clarification requests are highlighted inline). Three themes share the exact same controller and
sealed-term mechanic — only the personas and task change:

```
python run_demo.py --scenario firstcontact   # two civilizations with NO shared language at all
python run_demo.py --scenario spacecraft      # Mission Control vs Life Support, clashing jargon
python run_demo.py --scenario vendor          # the original procurement vs compliance scenario
```

**First Contact** is the purest form of the idea: the two sides start with zero words in common and
have to invent and clarify every shared term from scratch to strike a trade. **Spacecraft** shows it
generalizes — two experts who share a language but not a vocabulary negotiate an emergency maneuver
under a deadline. Requires `DASHSCOPE_API_KEY` in the environment.

## Deployment

- **Local (dev)**: `run_negotiation.py` / `run_baseline.py`, dictionary backed by a local JSON
  file, `DASHSCOPE_API_KEY` read from the shell environment.
- **Alibaba Cloud**: `fc_handler.py` (Function Compute entrypoint) + `store_redis.py`
  (`RedisDictionaryStore` against ApsaraDB for Redis), deployed via `s.yaml`
  (Serverless Devs, region `ap-southeast-1`). See [`DEPLOY.md`](DEPLOY.md) for the deploy steps.

## Repo layout

```
agents/                 Agent personas + Qwen client wrappers
  base.py               procurement / compliance (the measured experiment)
  base_baseline.py      same personas with a full schema known upfront
  base_firstcontact.py  two civilizations with no shared language (demo)
  base_spacecraft.py    mission control vs life support (demo)
controller.py           TurnController — pidgin negotiation loop, seal/reveal enforcement
controller_baseline.py  BaselineController — structured-schema negotiation loop
dictionary/             Shared dictionary store (local JSON + Redis-backed variants)
tasks/                  Seeded negotiation scenarios
run_negotiation.py      CLI: single pidgin negotiation
run_baseline.py         CLI: single baseline negotiation
run_demo.py             CLI: live streamed demo (firstcontact / spacecraft / vendor)
run_all_tasks.py        Runs both arms across all tasks, writes logs/summary.json
generate_dashboard.py   Rebuilds docs/dashboard.html from the logs
fc_handler.py           Alibaba Cloud Function Compute entrypoint
s.yaml                  Serverless Devs deploy config
DEPLOY.md               Step-by-step Alibaba Cloud deployment guide
docs/architecture.svg   Architecture diagram
docs/dashboard.html     Results dashboard (generated)
docs/VIDEO_SCRIPT.md    Demo video script
```

## License

MIT — see [LICENSE](LICENSE).
