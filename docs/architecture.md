Architecture Overview

Flow
- Alfred Script Filter (`alfred_filter.py`) parses the query with `utils/directives.py`.
- Router (`providers/router.py`) selects provider and validates tools.
- Action (`alfred_action.py`) resolves/creates a thread via `store.py`, builds context, calls the provider client, and persists messages.
- Clients (`providers/*_client.py`) normalise request/response to a common shape.

Data Model
- `threads(id, provider, model, name, created_at, updated_at)`
- `messages(id, thread_id, role, content, meta, created_at)`

Directive Mapping
- `@gpt-4o`, `@o4-mini`, `@claude-3-7-sonnet` → `model`
- `@provider:openai|anthropic` → explicit provider (optional)
- `@temp:0.6`, `@max:800`, `@sys:"..."`, `@name:...`, `@new`, `@cont`
- `@tools:browse,code,python` → validated per provider

Provider Capability Table (example)
- openai: tool_use=True, tools={browse, code, python}
- anthropic: tool_use=True, tools={browse, code}

Normalised Message Shape
- messages: list of {role: user|assistant|tool|system, content: str}
- system prompt is passed as `system` param (separate from messages)

Error Handling & Logging
- Clear messages for missing API keys, unknown models, dropped tools
- Rotating log (`aifred.log`) with meta only unless `AIFRED_DEBUG=1`

Testing
- `tests/test_directives.py` and `tests/test_router.py`
- `AIFRED_DRY_RUN=1` for local smoke testing without external calls

