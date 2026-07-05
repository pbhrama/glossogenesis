# Demo Video Script — Glossogenesis (1–3 min)

Target length: ~2:00. Track: Agent Society. Narration is what you say; [SCREEN] is what to show.
The demo hits the live API, so each round takes a couple seconds — either record it and trim the
dead air, or let the "thinking" pauses play as natural pacing.

Run the demo with:  `.venv/bin/python run_demo.py --scenario firstcontact`

---

## 0:00–0:20 — The hook

[SCREEN: title card or the repo README]

> "Most multi-agent AI systems cheat: every agent is handed the same data format before they
> ever talk. Glossogenesis asks what happens when you take that away. Two AI agents, no shared
> vocabulary, a tight word budget — and they have to invent their own shared language to get
> anything done."

---

## 0:20–1:30 — The demo: First Contact

[SCREEN: Terminal at the First Contact intro. Press Return to start.]

> "Two civilizations meet with literally no words in common. One wants to trade energy for the
> right to mine minerals the other holds sacred. They share nothing — so every term has to be
> invented and then explicitly explained before the other side can use it."

[SCREEN: let the rounds stream in one at a time. Point at a purple 'coins' tag early on.]

> "Watch round one — they coin a word for 'energy' and a word for 'the deep stone.' The purple
> tag is a brand-new word. But the other side can't just use it — see the cyan tag — it has to
> spend a whole turn asking what it means. That cost is the whole point: a new word isn't free."

[SCREEN: scroll to the convergence at the end.]

> "And by the end they've built an entire shared tongue from scratch — and reached an accord in a
> language neither of them started with. That's emergent communication, enforced in code, not
> just asked for in the prompt."

---

## 1:30–1:55 — The result (why it matters)

[SCREEN: open docs/dashboard.html]

> "One conversation is a party trick. The real result is that the invented vocabulary pays off.
> Across five tasks, the agents spend clarification rounds building their dictionary on the first
> task, then reuse it for free on every task after. Clarification cost drops from three to zero
> and stays there — a measurable learning curve."

[SCREEN: the learning-curve line chart, then the dictionary table.]

> "And I'm honest about the limits — raw round counts are noisy because some negotiations are just
> harder than others, so the clean metric is clarification rounds saved."

---

## 1:55–2:05 — Close

[SCREEN: architecture diagram or repo]

> "Enforced constraint, a real baseline to compare against, all running on Qwen Cloud.
> Glossogenesis — agents that build their own language, and get faster the more they use it."

---

## Optional second example
If you have time and want to show it generalizes, run
`.venv/bin/python run_demo.py --scenario spacecraft` — Mission Control vs Life Support negotiating
an emergency burn in orbital-mechanics vs crew-survival jargon. Keep the total under 3:00.

## Shot checklist
- [ ] Terminal recording of First Contact (full run, or trimmed to rounds 1–2 + the ending)
- [ ] Screen recording of docs/dashboard.html (stat tile → learning-curve chart → dictionary table)
- [ ] A glance at docs/architecture.svg
- [ ] Keep it under 3:00 (hard cap per the rules)
