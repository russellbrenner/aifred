Project TODO Roadmap

Implement Now
- [x] Unify config defaults across modules (utils/config.py)
- [x] Add token budgeting and history trimming (utils/budget.py)
- [x] Optional macOS notifications via env flag (utils/notify.py)
- [x] Improve logger to use Alfred data path when available
- [x] Expand tests: config, budget, action with trimming
- [x] Tool schema mapping and payload inclusion for OpenAI/Anthropic
- [x] Gemini function tools and tool_calls normalization
- [x] Perplexity options (citations, recency, depth, domain)
- [x] OpenRouter client + headers

Nice-to-Have (need input)
- [ ] Real Gemini-native tool execution chain (execute and pass results)
- [ ] Token estimation via provider tokenizers (ok to add deps like tiktoken?)
- [ ] Packaging script to build .alfredworkflow (preferred distribution flow?)
- [ ] Settings UI/commands to toggle options (e.g., copy-to-clipboard, notify)
- [ ] Metrics dashboard (local) for usage stats (acceptable?)
- [ ] Multi-profile support (work/personal), quick switch in Alfred

Later
- [ ] Streaming responses and live progress indicators
- [ ] Provider catalog fetch (OpenRouter, etc.) and dynamic model lists
- [ ] Export/share thread in Markdown/HTML
- [ ] Import from other providers (e.g., local LLMs)
