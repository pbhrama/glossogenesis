# Demo Video Script — Glossogenesis (1–3 min)

Target length: ~2:30. Track: Agent Society. Narration is what you say; [SCREEN] is what to show.
Record the two scenarios ahead of time (they take a bit as they hit the live API) so you can
scrub to the good parts, or run them live if you're comfortable with the pauses.

---

## 0:00–0:20 — The hook

[SCREEN: title card or the repo README]

> "Most multi-agent AI systems cheat: every agent is handed the same data format before they
> ever talk. Glossogenesis asks what happens when you take that away. Two AI agents, no shared
> vocabulary, a tight word budget — and they have to invent their own shared language to get
> anything done."

---

## 0:20–1:10 — Demo 1: First Contact (the showpiece)

[SCREEN: Terminal, First Contact intro screen. Press Return to start.]

> "Here, two civilizations meet with literally no words in common. One trades energy for the
> right to mine minerals the other holds sacred. They share nothing — so every term has to be
> coined and then explicitly clarified before it can be used."

[SCREEN: let the transcript scroll. Point at an early coined term.]

> "Watch round one — they coin 'light-flow' and 'deep-stone.' The other side can't just use
> those; it has to spend a turn asking what they mean. That question costs a round. That's the
> whole mechanic: coin a term, it's sealed, the other side pays to unlock it, then it's shared
> for free."

[SCREEN: scroll to the end where it converges.]

> "By the end they've built a whole shared tongue — 'ancestor-bone,' 'outer-deep,' 'watcher-
> stone' — and reached an accord in a language neither of them started with."

---

## 1:10–1:55 — Demo 2: Spacecraft (shows it's general)

[SCREEN: press Return for demo 2, Spacecraft intro.]

> "Same engine, totally different domain. A damaged spacecraft: Mission Control thinks in orbital
> mechanics, Life Support thinks in crew survival. Same events, different jargon — so they still
> have to build shared shorthand, under a deadline before comms blackout."

[SCREEN: let it run; point at the concrete numbers near the end.]

> "And they don't just agree to agree — they settle real constraints: a 2.8g burn, under 110
> seconds, finishing twelve minutes before blackout, with abort authority assigned. A genuine
> negotiation, not a rubber stamp."

---

## 1:55–2:20 — The result (why it matters)

[SCREEN: open docs/dashboard.html]

> "The point isn't one conversation — it's that the invented vocabulary pays off. Across five
> tasks, the agents spend clarification rounds building their dictionary on the first task, and
> then reuse it for free on every task after. Clarification cost drops from three to zero and
> stays there. That's a measurable learning curve."

[SCREEN: the learning-curve line chart, then the dictionary table.]

> "And I'm honest about the limits — raw round counts are noisy because some negotiations are just
> harder than others, so the clean metric is clarification rounds saved."

---

## 2:20–2:30 — Close

[SCREEN: architecture diagram or repo]

> "The constraint is enforced in code, not just asked for in the prompt, there's a real baseline
> to compare against, and it all runs on Qwen Cloud. Glossogenesis — agents that build their own
> language, and get faster the more they use it."

---

## Shot checklist
- [ ] Terminal recording of First Contact (full run, or trimmed to rounds 1–2 + the ending)
- [ ] Terminal recording of Spacecraft (trimmed to the intro + the numeric agreement at the end)
- [ ] Screen recording of docs/dashboard.html (stat tile → learning-curve chart → dictionary table)
- [ ] A glance at docs/architecture.svg
- [ ] Keep it under 3:00 (hard cap per the rules)
