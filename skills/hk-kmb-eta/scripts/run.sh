#!/usr/bin/env bash
for f in .claude/skills/hk-kmb-eta/scripts/query.py .agents/skills/hk-kmb-eta/scripts/query.py .agent/skills/hk-kmb-eta/scripts/query.py skills/hk-kmb-eta/scripts/query.py; do
  [ -f "$f" ] && break
done
if [ -f "$f" ]; then
  python3 "$f" "$@"
else
  echo "ERROR=NO_SCRIPT"
fi
