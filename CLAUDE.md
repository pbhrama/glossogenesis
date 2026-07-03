# Glossogenesis

## What this is
Multi-agent negotiation system for Global AI Hackathon w/ Qwen Cloud (Track 3: Agent Society).
Two Qwen-powered agents with distinct domain vocabularies (Procurement-agent, Compliance-agent) 
negotiate a task under a strict token/message budget with NO shared schema upfront. This forces 
them to build a shared compressed "pidgin" dictionary over rounds.

## Core mechanic
- Each turn: agent sends a short message, capped by token budget
- Message can (a) reuse an already-agreed term from the shared dictionary, or 
  (b) introduce a new term, which costs the other agent an extra round to ask "what does X mean?"
- Shared dictionary = growing JSON key-value store, visible/logged every round
- Negotiation ends when both agents agree, or an Arbiter agent steps in after N failed rounds

## What we're measuring
- Baseline: same task solved via standard structured tool-calling/JSON schema
- Experimental: same task via pidgin protocol
- Metric: turns/tokens to convergence, tracked ACROSS multiple tasks to show a learning 
  curve (convergence should get faster as the dictionary matures) — this IS the core result

## Stack
- Model: Qwen Cloud, OpenAI-compatible SDK, base_url https://dashscope-intl.aliyuncs.com/compatible-mode/v1
- API key in DASHSCOPE_API_KEY env var — NOT persisted anywhere in repo/shell profile; must be
  exported manually each session (key lives in Qwen Cloud dashboard > API Keys, labeled
  "Devpost Hackathon", Pay-As-You-Go, format looks like `sk-ws-...` — that's normal for this
  provider, don't panic and treat it as suspicious again)
- Models: DECIDED — same model (qwen-plus) for both agents. Rationale: keeps the pidgin-emergence
  story clean (compression driven only by the budget/schema constraint, not a capability gap
  between agents). Already the default in agents/base.py, no code change needed.
- Orchestration/dictionary store: eventually deployed on Alibaba Cloud (ECS/Function Compute + 
  Tablestore or Redis) — NOT yet, build and test locally first
- Frontend: simple dashboard, live dictionary + convergence graph (later)

## Current phase
Local negotiation loop (agents, controller, dictionary store) is BUILT AND VALIDATED against the
live API — see "Progress log" below. Currently deciding model config (same vs asymmetric) before
building the baseline comparison arm. No cloud deployment yet.

## Biggest risk
Make sure pidgin emergence is genuine (real hard constraints forcing compression), not scripted/
theater. Constraints need teeth or the demo is fake.
- RESOLVED (was a real bug, not just a theoretical concern): the original clarification-match
  logic (`term.lower() in incoming.lower()`) auto-unsealed every coined term exactly one round
  after coining, unconditionally — because the coining agent's own message necessarily contains
  the term's text, so the substring check always matched immediately regardless of whether the
  listener asked anything. The "costs a round to ask" rule had zero teeth. Fixed by adding an
  explicit `asking_about` field to the JSON response schema (agents/base.py) and having
  controller.py only reveal a sealed term when the CURRENT round's output explicitly lists it in
  `asking_about` (and not for a term the same speaker just coined this same turn). Re-validated
  live: round 2 now shows a genuine "what does 'PO' mean?" request before resolution, and
  convergence took 6 rounds instead of the old (fake) 4.

## Progress log
1. DONE — Built agents/base.py (QwenAgent, Procurement/Compliance system prompts, JSON response
   schema), dictionary/store.py (JSON-backed shared term store), controller.py (TurnController
   with sealed-term enforcement), run_negotiation.py (CLI), one seeded task
   (tasks/task_01_vendor_onboarding.json).
2. DONE — Committed to git locally (root commit 8d3b5cb, "Initial negotiation loop..."). Repo has
   NO remote configured — nothing has been pushed anywhere.
3. DONE — Ran run_negotiation.py against the live Qwen API on task_01. Result: converged in 4
   rounds, 1 clarification round, dictionary size 1. Confirmed the seal/reveal mechanic actually
   fires (term "data residency addendum" coined, sealed, later resolved). Full transcript in
   logs/task_01_run.jsonl (gitignored). Cost was negligible (small token budget, ~4 API calls).
4. DONE — Decided model config: same model (qwen-plus) for both agents. No code change needed
   (already the default).
5. DONE — Found and fixed the clarification-match bug (see "Biggest risk" above). Re-validated
   live against task_01: seal mechanic now genuinely binding. NOT YET COMMITTED to git.
6. DONE — Committed clarification-fix (commit 73913aa).
7. DONE — Built the baseline comparison arm: agents/base_baseline.py (BaselineAgent, full shared
   structured schema known upfront -- po_cap_usd / data_residency_deadline_days /
   audit_trail_deadline_days / conditions -- no coined vocab, no sealing), controller_baseline.py
   (BaselineController, simple two-consecutive-agree convergence, no dictionary logic),
   run_baseline.py (CLI, mirrors run_negotiation.py). Validated live against task_01: converged
   in 4 rounds (vs. 6 for the pidgin arm on the same task, which paid 2 extra rounds to coin +
   clarify "PO"). NOT YET COMMITTED to git.
8. NEXT UP — commit the baseline arm, then write more task JSONs, build a multi-task runner that
   runs BOTH arms per task, carries the pidgin dictionary forward across tasks (baseline has
   nothing to carry forward by design), and tracks the convergence-speed learning curve as the
   core result. Then cloud deployment + dashboard + submission assets.

## Submission requirements (don't forget)
- Public repo w/ OSS license visible in About section
- Proof of Alibaba Cloud deployment (video + code file link)
- Architecture diagram
- ~3 min demo video (YouTube/Vimeo/Facebook)
- Text description + which track
