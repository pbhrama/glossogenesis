# Recording the demo video

Everything you need to record the 1–3 minute demo. Narration lines live in
[`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md).

## Before you start
- You need your Qwen API quota available (the live demo makes API calls). If the free tier is
  tapped out, check `home.qwencloud.com` → Billing/Usage for the reset date, or use a Token Plan
  (`sk-sp-...`) key if you have one.
- Set the key in your terminal:  `export DASHSCOPE_API_KEY="sk-your-key"`

## Run the demo
From the repo root:

```
./demo.sh              # all three scenarios, with a pause before each
./demo.sh medical      # or just one (medical | startup | security)
```

Each scenario streams round by round: speakers are color-coded, purple = a coined word,
cyan = asking what one means. Press RETURN to advance between scenarios.

Also open the dashboard in a browser for the "results" part of the video:
`open docs/dashboard.html`

## Record the screen (macOS, built-in)
1. Press **Cmd + Shift + 5** → capture toolbar appears.
2. Choose **Record Selected Portion** and frame the Terminal window (or Record Entire Screen).
3. Click **Options** → set **Microphone** to your mic so narration is captured.
4. Click **Record**. Stop from the menu-bar stop button, or Cmd + Shift + 5 again.
5. The `.mov` saves to your Desktop.

## Suggested flow (~2 min)
1. Start recording, Terminal ready but not yet started.
2. Narrate the hook, then hit RETURN and let **medical** (Doctor vs Insurance) stream. Point out a
   purple coin and a cyan ask.
3. Optionally show a second scenario (`startup` or `security`) briefly to prove it generalizes.
4. Switch to the dashboard, scroll through the learning-curve chart + dictionary table while
   narrating the result.
5. Stop.

## Finish
- Trim dead air (the "thinking..." pauses) in **QuickTime Player** → Edit → Trim.
- Keep it **under 3:00** (hard cap).
- Upload to YouTube/Vimeo (Unlisted is fine) and grab the link for the Devpost submission.
