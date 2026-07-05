# Glossogenesis — Written Summary

**Track:** Agent Society
**Repo:** https://github.com/pbhrama/glossogenesis

## Pitch

Two Qwen agents that share no vocabulary are put under a tight token budget and have to invent
their own shorthand to finish a negotiation. Glossogenesis measures whether that invented
shorthand actually pays off, and it does: once the agents build a small shared dictionary on the
first task, every task after it converges without paying to re-explain anything.

## The problem

Most multi-agent setups hand every agent the same schema before they start talking. That works,
but it skips a more interesting question: can agents build a shared language on their own when
nobody agreed on a protocol first, and is it worth the effort? That situation comes up any time
agents from different systems have to deal with each other without a pre-agreed contract, like
marketplaces or cross-organization negotiation.

## What it does

There are two agents, a Procurement agent and a Compliance agent, on opposite sides of a
negotiation. The tasks are ordinary business scenarios: vendor onboarding, an expedited shipment,
adding a subcontractor, changing payment terms, and a data export request. The agents don't share
a schema, and every message costs tokens, so spelling everything out in full is expensive. That
pressure is what pushes them to make up short terms for ideas that keep coming up.

The main mechanic is a sealed-term rule that the controller enforces in code, not in the prompt:

- When an agent makes up a new term, it is sealed. The other agent can't use it until it asks what
  the term means, and asking costs a round.
- After that, the term goes into a shared dictionary and is free to reuse for the rest of the run
  and on later tasks.

I want to call out that this rule is real and not for show. An early version had a bug where a
substring match auto-unsealed every term one round after it was coined, so the "it costs a round
to ask" rule never actually fired. I found it, added an explicit `asking_about` field to the
response format, and confirmed that clarification now costs a real round.

To have something to compare against, there's a baseline arm: same agents, same model, same tasks,
but this time they get the full schema up front with no coining and no sealing. `run_all_tasks.py`
runs both arms on all five tasks, keeps the pidgin dictionary from one task to the next, and writes
the results to a log.

## The result

Over the five tasks, the pidgin arm spends 3 clarification rounds on the first task and 0 on every
task after that. The three terms it builds on task one get reused for free from then on. That is
the learning curve: the agents get more efficient as their shared vocabulary fills in.

The round counts themselves don't drop in a clean line (11, 5, 7, 4, 11), and I'm not going to
pretend they do. How many rounds a task takes depends a lot on how hard the negotiation itself is,
separate from vocabulary. So the honest metric is clarification rounds saved, not total rounds, and
the dashboard shows both.

## Technical notes

- Runs on Qwen Cloud through the OpenAI-compatible SDK, using `qwen-plus` for both agents. Using
  the same model on both sides is deliberate, so that any difference in convergence speed comes
  from the vocabulary constraint and not from one agent being smarter than the other.
- The protocol lives in the controller with a structured JSON response format, so the constraint
  can't be talked around by the model.
- The dictionary store is swappable. There's a local JSON version and a Redis version that share
  the same interface, so the same code runs locally or against ApsaraDB for Redis unchanged.
- For deployment there's a Function Compute handler (`fc_handler.py`) with a Serverless Devs
  config (`s.yaml`), plus a Simple Application Server path, all written up in `DEPLOY.md`.
- The results dashboard (`docs/dashboard.html`) is generated from the logs by
  `generate_dashboard.py` and shows the convergence charts, the learning curve, and the current
  shared dictionary.

## Why it matters

Agents that can compress how they talk to each other under a budget, and then reuse that
compression later, hold up better than agents pinned to a schema someone wrote by hand. That's a
useful property for any agent society that has to negotiate at scale. Glossogenesis is a small,
measurable demonstration that it happens, plus a harness (the baseline arm, the multi-task runner,
the dashboard) for putting a number on it.
