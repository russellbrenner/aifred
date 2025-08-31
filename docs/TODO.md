Project TODO Roadmap

Implement Now
- [x] Unify config defaults across modules (utils/config.py)
- [x] Add token budgeting and history trimming (utils/budget.py)
- [x] Optional macOS notifications via env flag (utils/notify.py)
- [x] Improve logger to use Alfred data path when available
- [x] Expand tests: config, budget, action with trimming
- [x] Tool schema mapping and payload inclusion for OpenAI/Anthropic

Nice-to-Have (need input)
- [ ] Real tool execution loop (execute tool_calls, append tool results, re-send)
- [ ] Token estimation via provider tokenizers (ok to add deps like tiktoken?)
- [ ] Packaging script to build .alfredworkflow (preferred distribution flow?)
- [ ] Settings UI/commands to toggle options (e.g., copy-to-clipboard, notify)
- [ ] Metrics dashboard (local) for usage stats (acceptable?)
- [ ] Multi-profile support (work/personal), quick switch in Alfred

Later
- [ ] Streaming responses and live progress indicators
- [ ] Export/share thread in Markdown/HTML
- [ ] Import from other providers (e.g., local LLMs)
