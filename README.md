# Aifred

AI conversation manager for Alfred that lets you initiate and continue chats with OpenAI and Anthropic models, control models and temperature via lightweight @directives, and keep your history private and local.

[![Alfred Gallery](https://img.shields.io/badge/Alfred-Gallery-blue)](https://alfred.app)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Table of Contents
- Features
- Requirements
- Installation
  - Quick Start
  - Configure Alfred Nodes
  - Environment Variables
- Usage
  - Directive Cheatsheet
  - Examples
  - Thread Management
- Provider Notes & Tools
- Testing
- Troubleshooting & FAQ
- Privacy & Security
- Development
- Contributing
- License

## Features

- Dual providers: OpenAI + Anthropic via a common interface
- Inline controls: `@gpt-4o @temp:0.6 @max:800 @tools:browse,code`
- Threads: Persist and resume per provider/model with names
- Alfred UX: Script Filter to send/continue + clear output and notifications
- Tool hints: Provider-native tool-use where supported; graceful fallback
- Privacy-first: Local SQLite; API keys via Alfred env vars

## Requirements

- macOS 10.15+
- Alfred 4+ with Powerpack
- Python 3.8+ (development target 3.12)

## Installation

### Quick Start
1) Clone and install dependencies
```bash
git clone https://github.com/russellbrenner/aifred.git
cd aifred
python3 setup.py
```
2) Set workflow environment variables (Alfred Preferences → Workflows → Aifred → [𝒾] icon → Environment Variables):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- Optional defaults: `AIFRED_PROVIDER_DEFAULT=openai`, `AIFRED_MODEL_DEFAULT_OPENAI=gpt-4o`, `AIFRED_MODEL_DEFAULT_ANTHROPIC=claude-3-7-sonnet`
- Optional extras: `AIFRED_SYSTEM_PROMPT_PATH`, `AIFRED_DB_PATH`, `AIFRED_DRY_RUN=1`, `AIFRED_COPY_CLIPBOARD=1`
  Additional controls: `AIFRED_MAX_INPUT_TOKENS=4000`, `AIFRED_NOTIFY=1`

3) Configure nodes in Alfred (see below) and start typing `ai`.

### Configure Alfred Nodes
Create this minimal workflow:
- Script Filter
  - Keyword: `ai`
  - Language: `/bin/bash` or `/usr/bin/python3`
  - Script: `/usr/bin/python3 "$PWD/alfred_filter.py" "{query}"`
  - with input as argv
- Run Script (connected from Script Filter)
  - Language: `/bin/bash` or `/usr/bin/python3`
  - Script: `/usr/bin/python3 "$PWD/alfred_action.py" "{query}"`
  - with input as argv

The Script Filter emits Alfred items where `arg` is a compact JSON payload consumed by the Run Script node.

Note: If your Python is at a different path (e.g., Homebrew), adjust `/usr/bin/python3` accordingly.

### Environment Variables
- `OPENAI_API_KEY` (required for OpenAI)
- `ANTHROPIC_API_KEY` (required for Anthropic)
- `AIFRED_PROVIDER_DEFAULT` = `openai` | `anthropic` (default: `openai`)
- `AIFRED_MODEL_DEFAULT_OPENAI` (default: `gpt-4o`)
- `AIFRED_MODEL_DEFAULT_ANTHROPIC` (default: `claude-3-7-sonnet`)
- `AIFRED_SYSTEM_PROMPT_PATH` (optional system prompt file)
- `AIFRED_DB_PATH` (optional; else Alfred data dir or `./aifred.db`)
- `AIFRED_DRY_RUN=1` (stub responses for local tests)
- `AIFRED_COPY_CLIPBOARD=1` (copy assistant replies to clipboard)
- `AIFRED_MAX_INPUT_TOKENS` (approximate cap for input history; default 4000)
- `AIFRED_NOTIFY=1` (show macOS notifications on send)
- `AIFRED_TOOL_EXEC=1` (execute tool_calls once and re-send)
- `AIFRED_PROFILE` (logical profile name; default `default`)
- `AIFRED_STREAM=1` (enable streaming for OpenAI requests, internal accumulation)
- `AIFRED_LEGAL_MODE=1` (enable default legal-research tools when not specified)

## Usage

### Alfred
- `ai` → List recent threads.
- `ai <message with @directives>` → Top result “Send to {provider model}” plus recent threads.

### Inference Actions (like Ayai)
- Script Filter: `alfred_actions_filter.py` — keyword e.g. `ai-actions`.
  - Type instructions to generate a custom action or pick a preset.
  - Enter: copy result; Cmd-Enter: paste (replace selection); Alt-Enter: stream.
- Runner: `alfred_actions_run.py` — connected Run Script consuming `{query}` and `{clipboard}` or selected text.
  - By default, uses your provider defaults; outputs transformed text only.

### File Attachments (basic)
- `alfred_attach.py <file>` — Creates a new thread named after the file and posts a short summary (uses pandoc if available, plain text fallback).
  - You can wire this as a Universal Action in Alfred for quick “Attach Document”.

### Directive Cheatsheet
- `@gpt-4o`, `@o4-mini`, `@claude-3-7-sonnet` → model
- `@temp:0.7` → temperature
- `@max:1000` → max tokens (mapped per provider)
- `@sys:"You are helpful"` → system prompt override
- `@name:research` → name thread
- `@new` → force a new thread
- `@cont` → continue most recent (provider/model if specified)
- `@tools:browse,code,python,fetch_url,citation_extract,case_search` → request tools (provider-validated)
  - With `AIFRED_TOOL_EXEC=1`, supported tool calls execute once and are included in a follow-up response.
  - With `AIFRED_LEGAL_MODE=1` and no explicit tools, the default toolset is used: browse, fetch_url, citation_extract, case_search.

### Examples
```
Summarise this repo @gpt-4o @temp:0.5 @tools:browse
Draft release notes @claude-3-7-sonnet @max:1200 @name:notes
Continue @cont and refine the migration plan @temp:0.2
```

### Thread Management
- New threads: `@new` or any fresh send creates a new thread with the resolved provider/model.
- Continue: `@cont` resumes the latest thread for the resolved provider (and model if specified).
- Name: `@name:xyz` sets or updates the thread name.

## Provider Notes & Tools
- Routing: Model hint and/or `@provider` select OpenAI or Anthropic; otherwise defaults.
- Tools: Requested tools are validated per provider capability. Unsupported tools are dropped and noted in the reply header.
- Context: History is trimmed approximately to fit under `AIFRED_MAX_INPUT_TOKENS` (oldest first), while reserving part of the budget for completions.
- Tool schemas are included in requests (OpenAI function tools; Anthropic tool definitions). If `AIFRED_TOOL_EXEC=1`, basic tool execution is performed:
  - `web_search`: DuckDuckGo Instant Answer (JSON) with HTML fallback.
  - `fetch_url`: Fetches and extracts readable text from a URL (best-effort).
  - `citation_extract`: Extracts basic case and U.S.C. citations from provided text.
  - `case_search`: Queries CourtListener API for cases (best-effort, public API).
  Results are appended as tool messages and a second model call is made.

## Testing
Run all tests:
```bash
python3 -m unittest discover -s tests -v
```

Dry-run provider calls (no external API requests):
```bash
export AIFRED_DRY_RUN=1
python3 alfred_action.py '{"query":"hello @gpt-4o","directives":{}}'
```

## Troubleshooting & FAQ
- API key errors → Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in Alfred env vars.
- Unknown model → Falls back to defaults.
- Unsupported tools → Dropped with a short header note.
- Python path issues → Verify `/usr/bin/python3` or adjust node scripts accordingly.
- No output in Alfred → Run the Script Filter and Action scripts in Terminal to inspect errors.
- Settings changes not applied → Ensure you're using the Settings Script or restart Alfred after editing env vars.

## Settings (Optional UI)
Add a second workflow for settings:
- Script Filter with keyword `ai-settings` running `/usr/bin/python3 "$PWD/alfred_settings.py" "{query}"`.
- Connected Run Script executing `/usr/bin/python3 "$PWD/alfred_settings.py" "{query}"`.

This shows toggles for notifications, clipboard copy, current profile, and max input tokens. Settings persist to a local config file in the Alfred data directory and are merged with environment variables.

## Packaging
Build a distributable `.alfredworkflow`:
```bash
python3 build_workflow.py
open dist/aifred.alfredworkflow
```

## Privacy & Security
- Local Storage: All conversation data stored locally in Alfred-approved directories.
- API Keys: Stored in Alfred environment variables; never in code.
- No Tracking: No external analytics.

## Development
```
aifred/
├── aifred.py             # Legacy import/search + redact utility
├── alfred_filter.py      # Alfred Script Filter (list threads, prepare send payload)
├── alfred_action.py      # Action: resolve thread, call provider, persist
├── alfred_actions_filter.py # Inference Actions Script Filter
├── alfred_actions_run.py  # Inference Actions runner
├── alfred_attach.py       # Universal Action: attach & summarize document
├── alfred_settings.py    # Script Filter for settings UI (optional)
├── providers/
│   ├── router.py         # Provider routing + capability map
│   ├── openai_client.py  # OpenAI client (normalised)
│   └── anthropic_client.py # Anthropic client (normalised)
├── utils/
│   ├── directives.py     # @directive parser + summary
│   └── logger.py         # Minimal rotating logger
│   ├── budget.py         # Token estimation and trimming
│   ├── config.py         # Unified defaults and overrides
│   ├── notify.py         # macOS notifications
│   ├── tools.py          # Tool schemas
│   └── user_config.py    # Settings persisted in Alfred data dir
├── store.py              # SQLite layer (threads/messages)
├── tests/                # Unit tests (parser/router/store/action)
├── docs/architecture.md  # Data flow and mapping tables
├── assets/               # Icons and visual assets
├── info.plist            # Alfred workflow configuration (packaging)
├── requirements.txt      # Python dependencies
└── setup.py              # Installation script
├── actions/actions.json  # Preset inference actions
└── build_workflow.py     # Package .alfredworkflow
```

See [AGENTS.md](AGENTS.md) for the iterative development plan and adherence to Alfred community standards. For deeper architectural notes, read [docs/architecture.md](docs/architecture.md).

## Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT License - see [LICENSE](LICENSE)

— Built with ❤️ for the Alfred community
