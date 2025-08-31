# Agents & Repository Guide

This document explains how agents are used in this project, the key architectural patterns, and where to find authoritative contribution standards. It is intentionally concise and avoids duplicating content already covered in README.md and CONTRIBUTING.md.

## Agent Roles

- General-purpose agent: Multi-step design and implementation across research, import pipelines, search UX, and feature iteration.
- DevOps engineer agent: Packaging/distribution, Python dependency management, virtualenv handling, SQLite schema/migrations, and workflow automation.

## Core Implementation Patterns

```python
# Bang filters for search refinement
"!chatgpt" -> platform_filter = "chatgpt"
"!claude"  -> platform_filter = "claude"
"!fav"     -> favourite_filter = True
"!pin"     -> pinned_filter = True

# Alfred Script Filter JSON
{
  "items": [
    {
      "uid": "unique_id",
      "title": "Display title",
      "subtitle": "Additional info",
      "arg": "action_argument",
      "mods": {
        "alt": {"subtitle": "Alt action",  "arg": "alt_arg"},
        "cmd": {"subtitle": "Cmd action",  "arg": "cmd_arg"}
      }
    }
  ]
}

# SQLite schema (conversations)
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  title TEXT,
  platform TEXT,  -- 'chatgpt' | 'claude'
  created_at TEXT,
  updated_at TEXT,
  messages TEXT,  -- JSON blob
  is_favourite INTEGER DEFAULT 0,
  is_pinned INTEGER DEFAULT 0
);
```

## Content Workflow

1. Import: ChatGPT/Claude exports -> normalized SQLite records.
2. Search: Script Filter + bang parsing + fuzzy match.
3. Actions: Continue, favourite, pin via modifier keys.
4. AI: OpenAI/Anthropic calls with restored context.
5. Storage: Alfred paths, local-only, privacy-first.

## Project Structure

- aifred.py: Database management and import routines.
- alfred_filter.py: Script Filter entry for search.
- alfred_action.py: Action handlers and API calls.
- assets/: Icons and visuals (≥256×256px, retina-friendly).
- docs/: Additional usage/configuration docs.
- info.plist: Alfred workflow metadata and bundle configuration.
- requirements.txt: Pinned Python dependencies.
- setup.py: Automated setup and workflow configuration.

Note: Modules live at the repository root (no src/ directory).

## Dev Commands

- `python3 setup.py` – Install dependencies and configure workflow.
- `python3 aifred.py search <query>` – Exercise search.
- `python3 aifred.py import <platform> <file>` – Import exports.
- `python3 alfred_filter.py "<query>"` – Inspect Script Filter JSON.
- `python3 alfred_action.py "<action>"` – Test actions and API wiring.

## Coding Conventions

- Python 3.8+ with type hints; 4-space indentation.
- Classes: PascalCase; methods/functions: snake_case; constants: UPPER_SNAKE_CASE.
- Follow Alfred Script Filter JSON schema exactly.
- Use parameterised SQL and proper connection handling.

For extended style and integration specifics, see CONTRIBUTING.md.

## Security & Privacy (Essentials)

- Store API keys in Alfred environment variables; never commit secrets.
- Keep all conversation data local under Alfred-approved paths.
- Do not bypass macOS security features; avoid unsigned binaries.

Comprehensive security and operational guidance lives in CONTRIBUTING.md.

## Alfred Community Standards (Integrated)

This project adheres to Alfred Workflow community best practices. Highlights:

- Clarity and style: Clear names, titles, and subtitles; follow the Alfred Gallery Style Guide.
- User configuration: Prefer Alfred environment variables for user options.
- Icons: Provide high-quality icons ≥256×256px.
- Feedback: Show progress/"Please wait" for remote or long operations.
- Data paths: Use Alfred support/cache paths (e.g., `alfred_workflow_data`).
- Error handling: Fail gracefully with informative messages.

Refer to CONTRIBUTING.md for the full, authoritative checklist and links.

## Repository Standards

- Keep README.md current with install, usage, and dependency notes.
- Use branches and conventional commits (e.g., `feat:`, `fix:`, `docs:`).
- PRs: Provide a clear summary, relate issues, and include validation steps.
- Documentation: Link to Alfred docs where relevant; avoid duplicating long guidance.

### Quick Checklist

- [ ] README covers install/usage.
- [ ] CONTRIBUTING details standards and processes.
- [ ] Pinned dependencies in requirements.txt.
- [ ] Icons present in assets/ (≥256×256px).
- [ ] info.plist configured and documented.

If distributing binaries, ensure signing/notarisation (see CONTRIBUTING.md).

## aifred: agent instructions for iterative development

These instructions guide Codex/Claude to iteratively improve the aifred Alfred workflow so it can initiate and continue conversations with both ChatGPT and Claude, select models/temperature via lightweight @directives, and invoke platform-specific tools. Follow the workflow, coding standards, and commit discipline below.

### Objectives

1. Support two chat providers (OpenAI + Anthropic) with a common interface.
2. Allow quick in-query controls, e.g. @gpt-4o @temp:0.6 @max:800 @tools:browse,code with sensible defaults if omitted.
3. Maintain and resume conversation threads (per provider, per topic) via persistent storage.
4. Expose a clean Alfred UX: a filter for queries, an action for sending/continuing, and transient notifications for status/errors.
5. Provide provider-native "tool use" where available (e.g. function/tool calling for OpenAI; tool use for Claude), but degrade gracefully when unsupported.
6. Ship thoroughly commented code, frequent small commits, and instructional commit messages.

### Repository touchpoints

- aifred.py (entry; orchestration)
- alfred_filter.py (Script Filter JSON for Alfred results)
- alfred_action.py (handles action when a result is selected)
- aifred.db (SQLite, conversation state)
- requirements.txt, info.plist, assets/, docs/

### Milestones

1. Router and directive parser
2. Provider clients with defaults + override handling
3. Conversation store (SQLite) and thread model
4. Tool registry and provider capability mapping
5. Alfred UI passes: filter → action → notify
6. Tests + docs + examples

Implement in the above order unless a dependency requires re-ordering.

### Command and directive syntax

Users type natural language plus optional @directives:

- @gpt-4o, @o4-mini, @claude-3-7-sonnet → model choice
- @temp:0.7 → temperature
- @max:1000 → max tokens (provider term mapped internally)
- @sys:"You are a helpful…" → system prompt override (quoted)
- @name:research → conversation name (thread label)
- @new → force a new thread
- @cont → continue most recent thread in this provider/context
- @tools:browse,code,python → request tools from the provider's registry
- @provider:openai|anthropic → explicit provider (if model ambiguous)

If a directive is missing, use provider defaults.

Examples

    Summarise this repo's structure @gpt-4o @temp:0.5 @tools:browse

    Draft a release note for v0.2 @claude-3-7-sonnet @max:1200 @name:notes

    Continue @cont and refine the migration plan @temp:0.2

### Defaults

- Provider: OpenAI
- Model (OpenAI): gpt-4o
- Model (Anthropic): claude-3-7-sonnet
- Temperature: 0.4
- Max tokens: provider-sensible default (map to max_output_tokens for Anthropic)
- Tools: none
- System prompt: short assistant prompt stored in config (see below)

### Configuration

Read from environment variables (document in README.md):

- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- AIFRED_PROVIDER_DEFAULT (openai|anthropic)
- AIFRED_MODEL_DEFAULT_OPENAI
- AIFRED_MODEL_DEFAULT_ANTHROPIC
- AIFRED_SYSTEM_PROMPT_PATH (optional path to a system prompt file)
- AIFRED_DB_PATH (defaults to ./aifred.db)

Fail early with human-readable error if required keys are missing.

### Conversation model

SQLite schema (migrate automatically if missing):

    CREATE TABLE IF NOT EXISTS threads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      provider TEXT NOT NULL,
      model TEXT NOT NULL,
      name TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );
    
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      thread_id INTEGER NOT NULL,
      role TEXT NOT NULL,          -- system|user|assistant|tool
      content TEXT NOT NULL,       -- raw text (JSON for tool calls if needed)
      meta JSON,                   -- tokens, tool info
      created_at TEXT NOT NULL,
      FOREIGN KEY(thread_id) REFERENCES threads(id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);

Rules:

- @new creates a new thread with selected provider/model.
- @cont resolves to the most recent thread matching provider (and model if set).
- @name:x sets or updates the thread's name.
- Always persist both user prompt and assistant response.

### Router

Implement a small router module:

    class ProviderCapability(TypedDict):
        tool_use: bool
        tool_names: set[str]  # e.g. {"browse","code","python"}
    
    class ProviderClient(Protocol):
        def send(self, system:str, messages:list[dict], model:str, temperature:float,
                 max_tokens:int|None, tools:list[str]) -> dict: ...
        def name(self) -> str: ...
    
    def route(model_hint: str|None, provider_hint: str|None) -> str:
        # returns "openai" or "anthropic" using model prefixes/known sets

- Map model names to providers.
- Validate requested tools against provider capabilities; warn and drop unsupported tools.

### Tool registry

Abstract tool requests to a neutral set; map per provider:

- browse → OpenAI: enable web tool if available; Anthropic: enable tools=[{"type":"web_search"}] when supported; otherwise ignore with an in-chat note.
- code → send "computer use"/"code" tool when supported; otherwise ignore.
- python → not executed locally; forward as a tool hint (only if provider supports a code interpreter). If unsupported, respond that the provider lacks that tool.

Always describe, in comments, how each tool is translated or disabled for each provider.

### Provider clients

Create providers/openai_client.py and providers/anthropic_client.py:

- Each client:
    - Accepts system, messages (role/content), model, temperature, max_tokens, tools.
    - Builds the provider-specific request.
    - Handles streaming off initially; implement non-streaming first.
    - Normalises the response to { "text": "...", "tool_calls": [...], "usage": {...} }.

Comprehensive inline comments on request/response mapping and any constraints.

### Directive parser

Implement a robust parser with quoted values:

- Parse tokens matching @key:value, @key:"quoted value", and bare @flag.
- Keys to support: gpt-* or claude-* (treated as model), temp, max, provider, name, cont, new, tools, sys.
- Strip directives from the final user message before sending.

Unit tests for directive parsing edge cases (quoted strings, multiple directives, duplicates where later wins).

### Alfred integration

- alfred_filter.py:
    - Present recent threads as results when no query text provided (show provider/model/name + updated time).
    - When query text exists, show top option "Send to {provider/model}" with parsed directives summary (temp, max, tools), plus a few recent threads for quick continue.
    - Output Script Filter JSON with arg as a compact JSON payload {query, directives, thread_hint}.
- alfred_action.py:
    - Receive the payload from filter.
    - Resolve thread via @cont/@new/@name.
    - Route provider/model, build system prompt, assemble context (last N messages or token-bounded history).
    - Call provider client.
    - Persist messages and show a notification on success/failure.
    - Optionally copy the assistant's text to clipboard (config flag).

Ensure graceful error messages surface in Alfred.

### Error handling

- Invalid API key → clear message suggesting how to set env var.
- Unknown model → fallback to provider default; attach a one-line notice to the assistant reply.
- Unsupported tools → drop and note in the assistant reply header.
- DB errors → retry once; on failure, show notification and write to a rotating log (./aifred.log).

### Logging

- Minimal rotating log with timestamped INFO/WARN/ERROR.
- Log only meta (provider, model, tokens count, directive summary). Do not log full prompt content unless AIFRED_DEBUG=1.

### Testing

Add a lightweight test harness (no external calls by default):

- Unit tests for directive parser and router.
- A "dry-run" mode that stubs provider responses for local smoke tests.

### Documentation

Update README.md:

- Installation, env vars, privacy note.
- Directive syntax cheatsheet with examples.
- Thread management (new/cont/name).
- Provider differences and tool support notes.
- Troubleshooting (keys, models, network).

Add docs/architecture.md explaining the data flow and mapping tables.

### Coding standards

- Python 3.12; type hints; docstrings on public functions.
- Keep modules small; one responsibility each.
- Extensive inline comments explaining provider mappings, token budgeting, and any non-obvious code.

### Commit discipline

Make small, incremental commits. Use present-tense, instructional messages that teach a newcomer what changed and why.

Template:

    feat(router): add provider router and model → provider mapping
    
    Explain:
    - Introduces route() that maps model hints to a provider.
    - Adds guardrails for unknown models (fallback to defaults).
    - Includes unit test skeleton and docstrings to aid new contributors.

Other examples:

    feat(parser): implement @directive parser with quoted values
    test(parser): add edge case coverage for @sys:"..." and duplicate keys
    docs: add directive cheatsheet to README
    refactor(db): create tables on startup and add indexes
    feat(openai): normalise response shape and usage stats
    feat(anthropic): initial client with tool capability descriptor
    feat(alfred): script filter shows threads + "send" action preview
    fix(action): preserve @name when continuing an existing thread

Commit at each independently running milestone (parser, router, client stubs, DB, Alfred filter, Alfred action, docs). Avoid "mega commits".

### Implementation notes and stubs

Provider capability table (example)

    PROVIDER_CAPS: dict[str, ProviderCapability] = {
        "openai": {"tool_use": True, "tool_names": {"browse","code","python"}},
        "anthropic": {"tool_use": True, "tool_names": {"browse","code"}},
    }

Normalised message shape

    Message = TypedDict("Message", {"role": str, "content": str})
    History = list[Message]  # ["system","user","assistant","tool"]

System prompt

Load from AIFRED_SYSTEM_PROMPT_PATH if set; else use a minimal default aligned to your style. Allow override via @sys:"..." for one-off queries.

### Alfred UX polish (pass two)

- Show a small badge of selected model next to the result title (e.g. "gpt-4o", "sonnet").
- For threads, subtitle shows last directive summary used (e.g. temp 0.4 | tools: none).
- On successful send, show transient macOS notification "Sent to claude-3-7-sonnet (temp 0.4)".

### Security and privacy

- Do not persist API keys; read from env.
- DB contains prompts/responses; document this plainly.
- Provide aifred.py --redact utility to export a thread with API keys removed and optional content redaction for sharing.

### Definition of done (first cut)

- Queries with/without directives work for both providers.
- @new, @cont, @name behave as specified.
- Reasonable defaults apply when directives are absent.
- Unsupported tool requests are explained and safely ignored.
- Code is documented, type-checked, and minimally tested.
- README and architecture notes are up to date.

### Initial task list (execute in order)

1. Create utils/directives.py with parser + tests.
2. Create providers/router.py with model/provider mapping and tests.
3. Add providers/openai_client.py and providers/anthropic_client.py (request/response normalisation, no streaming).
4. Implement store.py (SQLite layer) with migrations and helpers.
5. Wire alfred_filter.py to list threads and prepare payloads.
6. Wire alfred_action.py to resolve thread, route provider, call client, persist messages.
7. Update README.md and add docs/architecture.md.
8. Add minimal logging and error surfaces.
