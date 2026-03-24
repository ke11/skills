#!/usr/bin/env bash
for f in .claude/skills/hk-tcsp-licence/scripts/query.sh .agents/skills/hk-tcsp-licence/scripts/query.sh .agent/skills/hk-tcsp-licence/scripts/query.sh skills/hk-tcsp-licence/scripts/query.sh; do
  [ -f "$f" ] && break
done
if [ -f "$f" ]; then
  bash "$f" "$@"
else
  echo "ERROR=NO_SCRIPT"
fi
