Project TODO Roadmap

Implement Now
- [ ] Unify config defaults across modules (utils/config.py)
- [ ] Add token budgeting and history trimming (utils/budget.py)
- [ ] Optional macOS notifications via env flag (utils/notify.py)
- [ ] Improve logger to use Alfred data path when available
- [ ] Expand tests: config, budget, action with trimming

Nice-to-Have (need input)
- [ ] Provider tool schemas and real tool-use mapping (specify which tools first?)
- [ ] Token estimation via provider tokenizers (ok to add deps like tiktoken?)
- [ ] Packaging script to build .alfredworkflow (preferred distribution flow?)
- [ ] Settings UI/commands to toggle options (e.g., copy-to-clipboard, notify)
- [ ] Metrics dashboard (local) for usage stats (acceptable?)
- [ ] Multi-profile support (work/personal), quick switch in Alfred

Later
- [ ] Streaming responses and live progress indicators
- [ ] Export/share thread in Markdown/HTML
- [ ] Import from other providers (e.g., local LLMs)

