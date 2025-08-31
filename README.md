# Aifred

AI conversation manager for Alfred that lets you initiate and continue chats with OpenAI and Anthropic models, select models and temperature via lightweight @directives, and keep your history locally.

[![Alfred Gallery](https://img.shields.io/badge/Alfred-Gallery-blue)](https://alfred.app)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- 💬 Dual providers: OpenAI + Anthropic via a common interface
- ⚙️ Inline controls: `@gpt-4o @temp:0.6 @max:800 @tools:browse,code`
- 🧵 Threads: Persist and resume per provider/model with names
- 🧭 Alfred UX: Script Filter to send/continue + notifications via output
- 🛠️ Tool hints: Provider-native tool-use where supported; graceful fallback
- 🔐 Privacy-first: Local SQLite; API keys via Alfred env vars

## Installation

### From Alfred Gallery (Recommended)
1. Open Alfred Preferences → Workflows → Browse Gallery
2. Search for "Aifred"
3. Click "Install"

### Manual Installation
1. Download the latest [`.alfredworkflow` file](https://github.com/username/aifred/releases)
2. Double-click to install in Alfred
3. Run the setup: `python3 setup.py`

### Configuration
Set your keys and defaults in Alfred Workflow Environment Variables:
- `OPENAI_API_KEY` (required for OpenAI)
- `ANTHROPIC_API_KEY` (required for Anthropic)
- `AIFRED_PROVIDER_DEFAULT` = `openai` | `anthropic` (default: `openai`)
- `AIFRED_MODEL_DEFAULT_OPENAI` (default: `gpt-4o`)
- `AIFRED_MODEL_DEFAULT_ANTHROPIC` (default: `claude-3-7-sonnet`)
- `AIFRED_SYSTEM_PROMPT_PATH` (optional system prompt file)
- `AIFRED_DB_PATH` (optional; else Alfred data dir or `./aifred.db`)
- `AIFRED_DRY_RUN=1` (optional; stub responses for local tests)

## Usage

### Alfred
- `ai` → List recent threads.
- `ai <message with @directives>` → Top result “Send to {provider model}” plus recent threads.

### Directive cheatsheet
- `@gpt-4o`, `@o4-mini`, `@claude-3-7-sonnet` → model
- `@temp:0.7` → temperature
- `@max:1000` → max tokens (mapped per provider)
- `@sys:"You are helpful"` → system prompt override
- `@name:research` → name thread
- `@new` → force a new thread
- `@cont` → continue most recent (provider/model if specified)
- `@tools:browse,code,python` → request tools (provider-validated)

## Data Import (optional)

Legacy import of ChatGPT/Claude exports is still available via `aifred.py` for search-only workflows. The new threaded chat features use their own SQLite tables and don’t require imports.

## Requirements

### System Requirements
- macOS 10.15 or later
- Alfred 4+ with Powerpack license
- Python 3.8+ (dev target 3.12)

### Dependencies
- `requests` >= 2.31.0 (for API integration)
- `sqlite3` (included with Python)

All dependencies are automatically installed by the setup script.

## Privacy & Security

- Local Storage: All conversation data stored locally in Alfred-approved directories
- API Keys: Securely stored in Alfred environment variables
- No Tracking: No data collection or external analytics
- Open Source: Full source code available for audit

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors
```bash
git clone https://github.com/username/aifred.git
cd aifred
python3 setup.py
```

See [AGENTS.md](AGENTS.md) for development workflow and AI agent usage patterns. For deeper details, read [docs/architecture.md](docs/architecture.md).

## Development

### Project Structure
```
aifred/
├── aifred.py             # Legacy import/search commands
├── alfred_filter.py      # Alfred Script Filter (list threads, prepare send payload)
├── alfred_action.py      # Action: resolve thread, call provider, persist
├── providers/
│   ├── router.py         # Provider routing + capability map
│   ├── openai_client.py  # OpenAI client (normalised)
│   └── anthropic_client.py # Anthropic client (normalised)
├── utils/
│   ├── directives.py     # @directive parser + summary
│   └── logger.py         # Minimal rotating logger
├── store.py              # SQLite layer (threads/messages)
├── docs/                 # Additional documentation
├── assets/               # Icons and visual assets
├── info.plist            # Alfred workflow configuration
├── requirements.txt      # Python dependencies
└── setup.py              # Installation script
```

### Testing
```bash
# Unit tests
python3 -m unittest -v

# Dry-run provider calls (no external API requests)
export AIFRED_DRY_RUN=1
python3 alfred_action.py '{"query":"hello @gpt-4o","directives":{}}'
```

## Support

### Getting Help
- Documentation: Check `README.md` and `AGENTS.md`
- Bug Reports: Create an issue on GitHub
- Questions: Alfred Forum
- Feature Requests: GitHub Discussions

### Common Issues
- API key errors → Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in Alfred env vars.
- Unknown model → Falls back to defaults; a note prints in output.
- Unsupported tools → Silently dropped with a short header note.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Alfred team for the excellent workflow platform
- OpenAI and Anthropic for their AI APIs
- Community contributors and testers

---

Built with ❤️ for the Alfred community
