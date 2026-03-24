#!/usr/bin/env bash
for f in .claude/skills/hk-aed-wait/scripts/query.py .agents/skills/hk-aed-wait/scripts/query.py .agent/skills/hk-aed-wait/scripts/query.py skills/hk-aed-wait/scripts/query.py; do
  [ -f "$f" ] && break
done
if [ -f "$f" ]; then
  python3 "$f" "$@"
else
  echo "ERROR=NO_SCRIPT"
fi
