---
name: hk-aed-wait
description: "Fetch real-time A&E (Accident & Emergency) waiting times for Hong Kong public hospitals. Use this skill when the user asks about hospital waiting times, A&E queues, emergency room wait, which hospital is fastest, 急症室等候時間, 邊間醫院最快 — even casually like 而家急症等幾耐 or 去邊間急症好."
allowed-tools: [Bash]
disable-model-invocation: true
effort: low
argument-hint: "[hospital name] [en|tc|sc]"
---

Run this command and present the output directly as markdown:

```bash
f=.claude/skills/hk-aed-wait/scripts/query.py; [ -f "$f" ] || f=.agents/skills/hk-aed-wait/scripts/query.py; [ -f "$f" ] || f=.agent/skills/hk-aed-wait/scripts/query.py; [ -f "$f" ] || f=skills/hk-aed-wait/scripts/query.py; [ -f "$f" ] && python3 "$f" $ARGUMENTS || echo "ERROR=NO_SCRIPT"
```

Output is pre-formatted between `---BEGIN---` / `---END---` markers. Show it as-is.
