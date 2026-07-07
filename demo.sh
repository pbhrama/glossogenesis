#!/bin/zsh
# Glossogenesis live demo runner.
# Runs the three real-world negotiation scenarios one at a time, streaming each
# round live (color-coded speakers; coined words and clarifications highlighted).
#
# Usage:
#   export DASHSCOPE_API_KEY="sk-..."   # your Qwen Cloud key
#   ./demo.sh                            # all three scenarios, with pauses
#   ./demo.sh medical                    # a single scenario (medical|startup|security)
#
# Good for screen-recording the demo video (see docs/RECORDING.md).

cd "$(dirname "$0")"

if [[ -z "$DASHSCOPE_API_KEY" ]]; then
  print -P "%F{red}DASHSCOPE_API_KEY is not set.%f"
  echo "Run:  export DASHSCOPE_API_KEY=\"sk-your-key\"   then re-run ./demo.sh"
  exit 1
fi

PY=".venv/bin/python"
[[ -x "$PY" ]] || PY="python3"
LOGDIR="${TMPDIR:-/tmp}"

run_scene () {
  local scene="$1" title="$2" blurb="$3"
  clear
  print -P "%F{cyan}=========================================================%f"
  print -P "%F{cyan}  GLOSSOGENESIS  —  $title%f"
  print -P "%F{cyan}=========================================================%f"
  echo ""
  print -P "$blurb"
  echo ""
  print -P "%8FColor-coded speakers.  Purple = coins a new term.  Cyan = asks what one means.%f"
  echo ""
  read "?Press RETURN to run this scenario..."
  $PY run_demo.py --scenario "$scene" --budget 45 --max-rounds 26 --log "$LOGDIR/glosso_${scene}.jsonl"
  echo ""
}

# Single-scenario mode
if [[ -n "$1" ]]; then
  run_scene "$1" "${(U)1}" "One live negotiation."
  exit 0
fi

run_scene medical "DOCTOR vs INSURANCE" \
  "A physician and an insurance reviewer negotiate a patient's care plan.\nClinical vocabulary vs claims vocabulary."
print -P "%F{green}Care plan agreed.%f"
read "?Press RETURN for the next scenario..."

run_scene startup "FOUNDER vs INVESTOR" \
  "A startup founder and a VC negotiate a seed-round term sheet.\nProduct/growth vocabulary vs finance/deal vocabulary."
print -P "%F{green}Term sheet agreed.%f"
read "?Press RETURN for the next scenario..."

run_scene security "ENGINEER vs SECURITY" \
  "An engineer and a security reviewer negotiate a feature launch.\nDelivery vocabulary vs security-risk vocabulary."
print -P "%F{green}Launch plan agreed.%f"
echo ""
print -P "%F{cyan}Same engine every time: coin a term -> it's sealed -> the other%f"
print -P "%F{cyan}side pays a round to ask -> then it's shared for free.%f"
