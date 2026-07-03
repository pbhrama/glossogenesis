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
- API key in DASHSCOPE_API_KEY env var (already set)
- Models: qwen3.7-plus and/or qwen3.6-flash (deciding if agents should use same or asymmetric models)
- Orchestration/dictionary store: eventually deployed on Alibaba Cloud (ECS/Function Compute + 
  Tablestore or Redis) — NOT yet, build and test locally first
- Frontend: simple dashboard, live dictionary + convergence graph (later)

## Current phase
Building the negotiation loop locally first: agent prompts, turn controller (enforces token 
budget + clarification-cost rule), dictionary store (start as local JSON file). 
No cloud deployment yet.

## Biggest risk
Make sure pidgin emergence is genuine (real hard constraints forcing compression), not scripted/
theater. Constraints need teeth or the demo is fake.

## Submission requirements (don't forget)
- Public repo w/ OSS license visible in About section
- Proof of Alibaba Cloud deployment (video + code file link)
- Architecture diagram
- ~3 min demo video (YouTube/Vimeo/Facebook)
- Text description + which track
