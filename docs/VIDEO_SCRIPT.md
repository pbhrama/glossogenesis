# Demo Video Script — Glossogenesis (1–3 min)

Target length: ~2:00. Track: Agent Society. Narration is what you say; [SCREEN] is what to show.
The demo hits the live API, so each round takes a couple seconds — either record it and trim the
dead air, or let the "thinking" pauses play as natural pacing.

Run the demo with:  `.venv/bin/python run_demo.py --scenario medical`
(Other scenarios: `--scenario startup`, `--scenario security`.)

---

## 0:00–0:20 — The hook

[SCREEN: title card or the repo README]

> "Most multi-agent AI systems cheat: every agent is handed the same data format before they
> ever talk. Glossogenesis asks what happens when you take that away. Two AI agents that speak
> different professional languages, a tight word budget — and they have to build their own shared
> shorthand to get anything done."

---

## 0:20–1:20 — The demo: Doctor vs Insurance

[SCREEN: Terminal at the Doctor vs Insurance intro. Press Return to start.]

> "Here's a case anyone recognizes. A doctor wants an MRI and a specialist referral approved for a
> patient. An insurance reviewer decides what's covered. The doctor talks in clinical terms, the
> reviewer talks in claims terms — same decisions, different vocabulary — and every message is
> capped, so they can't just over-explain."

[SCREEN: let the rounds stream in one at a time. Point at a purple 'coins' tag.]

> "Watch — the doctor coins a shorthand for the patient's warning signs. The purple tag is a
> brand-new term. The reviewer can't just use it — see the cyan tag — it has to spend a turn
> asking what it means. That's the whole mechanic: a new term isn't free, it costs a round to
> establish, and after that it's shared."

[SCREEN: scroll to the convergence at the end.]

> "And they settle a real plan — approval now, in-network referral, documentation, a validity
> window — using vocabulary they built on the fly. The constraint is enforced in code, not just
> asked for in the prompt."

---

## 1:20–1:35 — Show it generalizes (optional, quick)

[SCREEN: quickly run or cut to `--scenario startup` or `--scenario security`.]

> "Same engine, any domain. A founder and an investor negotiating a term sheet. An engineer and a
> security reviewer shipping a feature. Different jargon every time — same behavior: build shared
> shorthand under pressure."

---

## 1:35–1:55 — The result (why it matters)

[SCREEN: open docs/dashboard.html]

> "One conversation is a party trick. The real result is that the invented vocabulary pays off.
> Across five negotiation tasks, the agents spend clarification rounds building their dictionary on
> the first task, then reuse it for free on every task after. Clarification cost drops from three
> to zero and stays there — a measurable learning curve."

[SCREEN: the learning-curve line chart, then the dictionary table.]

> "And I'm honest about the limits — raw round counts are noisy because some negotiations are just
> harder than others, so the clean metric is clarification rounds saved."

---

## 1:55–2:05 — Close

[SCREEN: architecture diagram or repo]

> "Enforced constraint, a real baseline to compare against, all running on Qwen Cloud.
> Glossogenesis — agents that build their own language, and get faster the more they use it."

---

## Shot checklist
- [ ] Terminal recording of the Doctor vs Insurance demo (full run, or trimmed to the coin/ask
      exchange + the ending)
- [ ] Optional quick cut to startup or security to show it generalizes
- [ ] Screen recording of docs/dashboard.html (stat tile → learning-curve chart → dictionary table)
- [ ] A glance at docs/architecture.svg
- [ ] Keep it under 3:00 (hard cap per the rules)
