# Aifred

> AI conversation manager for Alfred that imports your ChatGPT/Claude history and lets you search and continue conversations.

[![Alfred Gallery](https://img.shields.io/badge/Alfred-Gallery-blue)](https://alfred.app)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- 🔍 **Import & Search**: Import ChatGPT/Claude conversation exports with full-text search
- 💬 **Continue Conversations**: Load conversation context and continue where you left off
- 🏷️ **Smart Filtering**: Bang syntax (`!chatgpt`, `!claude`, `!fav`, `!pin`) for precise searches
- ⭐ **Conversation Management**: Favourite and pin important conversations
- 🔄 **Multi-Platform**: Support for ChatGPT and Claude with extensible architecture
- 🔐 **Privacy First**: All data stored locally in Alfred-approved directories

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
Set your API keys in Alfred Workflow Environment Variables:
- `OPENAI_API_KEY` - For ChatGPT integration
- `CLAUDE_API_KEY` - For Claude integration (optional)

## Usage

### Basic Commands
- `ai` - Show recent conversations and import options
- `ai <query>` - Search conversations or start new chat
- `ai import` - Access import functionality

### Search Syntax
- `ai machine learning` - Find conversations about machine learning
- `ai !chatgpt python` - Search only ChatGPT conversations for "python"
- `ai !claude !fav` - Show favourite Claude conversations
- `ai !pin` - Show all pinned conversations

### Keyboard Shortcuts
- `Enter` - Open/view conversation
- `⌥ + Enter` - Continue conversation with AI
- `⌘ + Enter` - Toggle favourite status
- `⌃ + Enter` - Toggle pin status

## Data Import

### ChatGPT Export
1. Visit [ChatGPT Settings](https://chatgpt.com/settings) → Data controls → Export data
2. Download your `conversations.json` file
3. Use `ai import chatgpt /path/to/conversations.json`
4. Wait for import completion message

### Claude Export
1. Visit Claude Settings → Export your data
2. Download the export file
3. Use `ai import claude /path/to/claude-export.json`
4. Conversations will be available immediately

### Supported Formats
- **ChatGPT**: Standard JSON export with conversation mapping
- **Claude**: JSON export with chat messages array
- **Future**: Support planned for additional AI platforms

## Requirements

### System Requirements
- macOS 10.15 or later
- Alfred 4+ with Powerpack license
- Python 3.8 or later

### Dependencies
- `requests` >= 2.31.0 (for API integration)
- `sqlite3` (included with Python)

All dependencies are automatically installed by the setup script.

## Privacy & Security

- **Local Storage**: All conversation data stored locally in Alfred-approved directories
- **API Keys**: Securely stored in Alfred environment variables
- **No Tracking**: No data collection or external analytics
- **Open Source**: Full source code available for audit

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors
```bash
git clone https://github.com/username/aifred.git
cd aifred
python3 setup.py
```

See [AGENTS.md](AGENTS.md) for development workflow and AI agent usage patterns.

## Development

### Project Structure
```
aifred/
├── src/
│   ├── aifred.py          # Core database and import functionality
│   ├── alfred_filter.py   # Search interface for Alfred
│   └── alfred_action.py   # Action handlers and AI integration
├── assets/               # Icons and visual assets
├── docs/                # Additional documentation
├── info.plist          # Alfred workflow configuration
├── requirements.txt    # Python dependencies
└── setup.py           # Installation script
```

### Testing
```bash
# Test core functionality
python3 aifred.py search "test query"

# Test Alfred integration
python3 alfred_filter.py "test query"

# Test actions
python3 alfred_action.py "test_action"
```

## Support

### Getting Help
- 📖 **Documentation**: Check `README.md` and `AGENTS.md`
- 🐛 **Bug Reports**: [Create an issue](https://github.com/username/aifred/issues)
- 💬 **Questions**: [Alfred Forum](https://www.alfredforum.com/)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/username/aifred/discussions)

### Common Issues
- **Import Fails**: Ensure export file is valid JSON and path is correct
- **API Errors**: Verify API keys are correctly set in workflow environment
- **Search Issues**: Check database was created successfully in Alfred data directory

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Alfred team for the excellent workflow platform
- OpenAI and Anthropic for their AI APIs
- Community contributors and testers

---

Built with ❤️ for the Alfred community