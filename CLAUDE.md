# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A multi-skill monorepo for Claude Code and other AI agents, distributed via [skills.sh](https://skills.sh).

## Architecture

Each skill is a standalone directory under `skills/`. A skill must contain a `SKILL.md` file and may optionally include supporting files (Python scripts, data files, etc.).

```
skills/
  hk-weather/
    SKILL.md              # Skill instructions (required)
  kmb-eta/
    SKILL.md              # Skill instructions (required)
    query.py              # Python query script
    data.json             # Bundled offline data
```

### Plugin Discovery

`.claude-plugin/plugin.json` has `"skills": ["./skills/"]` which auto-discovers all subdirectories and registers them as available skills. Adding a new skill requires only creating a new directory with `SKILL.md` — no config changes needed.

### Bilingual Documentation

- `README.md` — Traditional Chinese (primary)
- `README.en.md` — English

Both must be kept in sync. When updating documentation, update both files to maintain parity.

## SKILL.md Format

Each skill is defined by YAML frontmatter followed by markdown instructions:

```yaml
---
name: <skill-name>
description: "Brief description of what the skill does"
allowed-tools: [Bash, WebFetch, ...]
disable-model-invocation: true|false
argument-hint: "[optional args] [language code]"
---

# Instructions for Claude

Step-by-step guidance on how to implement the skill...
```

**Key frontmatter fields:**
- `name`: Skill identifier (lowercase, no spaces)
- `description`: One-line summary for skill listing
- `allowed-tools`: Array of tool names the skill is allowed to use. Set to an empty array `[]` if the skill contains all logic in instructions
- `disable-model-invocation`: Set to `true` if Claude should only follow the exact SKILL.md instructions without applying general reasoning
- `argument-hint`: Guidance for skill invocation syntax (shown in `/help` and skill suggestions)
- `model`: (optional) Override model for this skill — accepts aliases (`haiku`, `sonnet`, `opus`) or full model IDs
- `effort`: (optional) Override effort level — `low`, `medium`, or `high`

**Instruction Guidelines:**
- Use clear step-by-step instructions (Step 1, Step 2, etc.)
- Explain argument parsing upfront if the skill accepts arguments
- Include data fetch endpoints (URLs, API structure) with example curl commands
- Show error handling expectations ("if X fails, do Y")
- Provide exact output format templates with field names in `{braces}`
- Include formatting rules (date formats, number precision, field omission rules)

See `skills/weather/SKILL.md` for a detailed example with parallel API fetching, error handling, multi-language support, and complex output formatting.

## Adding a New Skill

1. Create a new directory: `skills/<skill-name>/`
2. Write `SKILL.md` with frontmatter and step-by-step instructions
3. Update both `README.md` and `README.en.md` with a new entry in the "Available Skills" section
4. The skill will be auto-discovered on next plugin reload

**Best Practices:**
- Keep instructions concise but complete—avoid vague language
- Test output format by hand-tracing the examples
- Use variables like `{updateTime}` to mark dynamic data points
- Explain what to do if an API endpoint fails
- Include language/locale handling if applicable
- If multiple endpoints are needed, use parallel fetches (background `&` + `wait`) to avoid sequential tool delays

## Common Patterns

**Parallel API Fetching**: When a skill needs multiple endpoints, fetch them simultaneously:
```bash
curl -s URL1 > /tmp/file1.json &
curl -s URL2 > /tmp/file2.json &
wait
# Process both files
```

**Error Handling**: If a curl request fails or returns invalid JSON, continue processing remaining endpoints rather than stopping.

**Language/Locale Switching**: Accept language codes in arguments (`en`, `tc`, `sc`) and pass them to API endpoints. Default to `tc` (Traditional Chinese) if not specified.

**Output Formatting**: Template output with clear section headers and tables. Omit null/empty fields silently—do not show placeholder text.

## Distribution

Skills are distributed via [skills.sh](https://skills.sh). Installation:
```bash
npx skills add ke11/skills --skill <skill-name>
```

The plugin.json metadata (name, version, description, homepage, repository, keywords) is used by the skills.sh registry.

## Current Skills

| Skill | Description |
|-------|-------------|
| `hk-weather` | Hong Kong Observatory real-time weather data |
| `kmb-eta` | KMB real-time bus ETA |

## API Endpoints Reference

### KMB Open Data API

Base URL: `https://data.etabus.gov.hk/v1/transport/kmb`

| Endpoint | Description | Used by |
|----------|-------------|---------|
| `GET /route/{route}/{direction}/1` | Route info (orig/dest names) | `kmb-eta` |
| `GET /route-stop/{route}/{direction}/1` | Stop sequence for a route | `kmb-eta` |
| `GET /stop` | All stops (bulk, ~6700 stops) | `kmb-eta` (bundled in data.json) |
| `GET /stop/{stop_id}` | Individual stop detail | — |
| `GET /eta/{stop_id}/{route}/1` | Real-time ETA | `kmb-eta` |

- `{direction}`: `outbound` or `inbound`
- All endpoints return JSON with `{ "type", "version", "generated_timestamp", "data" }` structure
- No API key required, read-only GET requests only

### Hong Kong Observatory Open Data API

Base URL: `https://data.weather.gov.hk/weatherAPI/opendata`

See `skills/weather/SKILL.md` for full endpoint list.
