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
8. DONE — Wrote 4 more tasks (tasks/task_02..05, varying Procurement/Compliance conflict
   scenarios: expedited shipment, subcontractor addition, payment terms change, data export).
   Built run_all_tasks.py: runs both arms per task, carries the pidgin DictionaryStore forward
   across tasks (fresh agent instances/history per task, but shared dictionary object), writes
   logs/summary.json. NOT YET COMMITTED to git.
9. DONE — Ran all 5 tasks live end to end. Results (see logs/summary.json):
   task_01: pidgin 11 rounds / 3 clarification, baseline 5 rounds, dict grows 0->3
   task_02: pidgin 5 rounds / 0 clarification, baseline 4 rounds (dict already at 3)
   task_03: pidgin 7 rounds / 0 clarification, baseline 4 rounds
   task_04: pidgin 4 rounds / 0 clarification, baseline 4 rounds
   task_05: pidgin 11 rounds / 0 clarification, baseline 4 rounds
   REAL SIGNAL: clarification cost drops to 0 after task_01 and stays there -- the 3-term
   dictionary built in task_01 gets reused for free afterward. This is the learning-curve
   story working as intended.
   HONEST CAVEAT: raw round count does NOT cleanly decrease (11,5,7,4,11) even though
   clarification cost does -- round count is also driven by how contentious each task's
   negotiation content is (e.g. task_05's cross-border legal scenario was just harder), not
   only vocabulary cost. For the submission, report clarification-rounds-saved as the clean
   metric, not raw round count, or run multiple reps per task and average to smooth noise.
10. DONE — Committed run_all_tasks.py + new tasks + logs/summary.json (commit c6f54eb).
11. DONE — Full self-audit after user asked "make sure nothing was messed up": confirmed no git
   remote exists (nothing pushable), working tree clean, API key never committed anywhere
   (grepped full history for the literal key value, zero matches), .gitignore actually excludes
   dictionary/shared_dictionary.json + logs/*.jsonl + .venv/, all 8 source files compile clean,
   git ls-files matches exactly what's expected. No issues found.
12. DONE — Added --reps flag to run_all_tasks.py to average multiple runs per task per condition
   (smooths round-count noise; only rep 0 advances the canonical pidgin dictionary, reps 1..N-1
   run against a scratch-cloned copy and are discarded). NOT YET RUN LIVE, NOT YET COMMITTED.
   DELIBERATELY DEFERRED — user decided to hold off on burning extra API calls for noise
   reduction until more of the project is built; will revisit closer to shipping.
13. DONE — Cloud deployment scaffolding built (user chose this over dashboard/submission-assets
   first, and chose "I write code, you deploy it" -- assistant never touched real Alibaba Cloud
   credentials or triggered real cloud spend):
   - dictionary/store_redis.py: RedisDictionaryStore, same interface as the local
     DictionaryStore, backed by ApsaraDB for Redis (standard `redis` package, no proprietary
     Alibaba SDK needed since ApsaraDB for Redis is protocol-compatible). Smoke-tested against
     fakeredis (in-memory emulator, dev-only dep in requirements-dev.txt) -- confirmed as a
     genuine drop-in for TurnController with a real live negotiation run.
   - fc_handler.py: Alibaba Cloud Function Compute entrypoint, runs one negotiation given
     {"task_id", "budget", "max_rounds"}, returns JSON transcript. Reads DASHSCOPE_API_KEY /
     REDIS_HOST / REDIS_PORT / REDIS_PASSWORD from FC environment variables (never hardcoded).
     Smoke-tested end-to-end locally (real Qwen API calls + fakeredis standing in for
     ApsaraDB) -- works, converged in 10 rounds on task_04 with a genuine clarification
     exchange.
   - s.yaml: Serverless Devs deploy config, region ap-southeast-1, HTTP-triggered FC function,
     env vars pulled from shell env at deploy time (not hardcoded, file is committed to git).
   - DEPLOY.md: step-by-step deploy guide for the USER to run themselves (create AccessKey,
     install Serverless Devs CLI, create ApsaraDB for Redis instance, set env vars, `s deploy`,
     test with curl, what to capture for the submission's proof-of-deployment requirement).
   - requirements.txt now includes redis>=5.0.0 (real prod dep); requirements-dev.txt adds
     fakeredis (local testing only, not deployed).
   - Committed to git (commit d9bd077, no co-author line per user preference -- see
     "Preferences" below).
15. PAUSED — actual deployment (running DEPLOY.md's steps) is blocked: user could not find
   Alibaba Cloud's AccessKey Management page. Turned out they were on the Qwen Cloud product
   dashboard (dashscope/model billing portal), not the full Alibaba Cloud console -- those are
   separate sites. Pointed them to https://home.console.aliyun.com as the real console entry
   point, but they still couldn't locate it there either. USER DECIDED TO SET THIS ASIDE FOR NOW
   and move on to other work. Cloud deployment code (fc_handler.py, store_redis.py, s.yaml,
   DEPLOY.md) is done and tested locally -- only the actual `s deploy` run (which requires the
   user's own AccessKey) remains, whenever they want to pick it back up.
16. NEXT UP — user chose to defer cloud deployment and work on other stuff instead. Candidates:
   dashboard (live dictionary + convergence graph), submission assets (public repo + license,
   architecture diagram, demo video, description), and the deferred noise-reduction reps
   (item 12). Ask user which one when resuming.

## Preferences
- Do NOT add a "Co-Authored-By: Claude..." trailer to git commit messages in this repo (user
  asked to remove it explicitly -- "get rid of any mention of claude").

## Submission requirements (don't forget)
- Public repo w/ OSS license visible in About section
- Proof of Alibaba Cloud deployment (video + code file link)
- Architecture diagram
- ~3 min demo video (YouTube/Vimeo/Facebook)
- Text description + which track
