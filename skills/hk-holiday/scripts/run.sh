#!/usr/bin/env bash
for f in .claude/skills/hk-holiday/scripts/query.py .agents/skills/hk-holiday/scripts/query.py .agent/skills/hk-holiday/scripts/query.py skills/hk-holiday/scripts/query.py; do
  [ -f "$f" ] && break
done
if [ -f "$f" ]; then
  python3 "$f" "$@"
else
  echo "ERROR=NO_SCRIPT"
fi
