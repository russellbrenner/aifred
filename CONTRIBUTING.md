# Contributing to Aifred

Welcome to Aifred! We appreciate your interest in contributing to this Alfred AI conversation management workflow.

## Alfred Workflow Contribution Guidelines

### General Best Practices

- **Clarity and Style**: Instructions, keywords, and node names must be clear, concise, and descriptive. Follow the [Alfred Gallery Style Guide](https://www.alfredapp.com/help/workflows/style-guide/).
- **User Configuration**: Support user-facing configuration options whenever possible through Alfred workflow environment variables.
- **Icons**: Use icons at least 256×256px for workflow visibility and professional appearance.

### Security and Safety

- **System Safety**: Never bypass macOS gatekeeping or automate post-install binaries. Only distribute signed, notarised binaries.
- **Privacy**: Do not collect user data without consent and avoid distributing sensitive exported configs. All conversation data remains local.
- **API Security**: Store API keys securely in Alfred environment variables, never in code or version control.

### Technical Maintenance

- **Dependencies**: Explicitly list all dependencies (`pip`, `brew`, etc.) in documentation and bundle essential libraries. Avoid opaque install steps.
- **Data Storage**: Store workflow data in recommended Alfred support/cache paths (`alfred_workflow_data`).
- **Remote Data**: Provide user feedback (e.g. "Please wait") during remote queries or data fetches.
- **Error Handling**: Implement graceful error handling with informative user messages.

### Community Collaboration

- **Testing and Feedback**: Share drafts with the Alfred Forum for bug reports and improvement before Gallery submission.
- **Issue Reporting**: Encourage users to report problems using structured issues with reproduction steps.

## GitHub Contribution Standards

### Repository Structure Requirements

- [x] Root folder contains clear `README.md` with installation and usage instructions
- [x] `CONTRIBUTING.md` present with contribution guidelines  
- [x] `AGENTS.md` documenting development workflow and AI agent usage
- [ ] Clear icon image (minimum 256×256px) in `assets/` directory
- [x] List of dependencies with installation details in `requirements.txt`
- [x] Workflow configuration documented in `info.plist`

### Commit Etiquette

- Use conventional commit format: `feat: add conversation search`, `fix: resolve import bug`, `docs: update README`
- Write clear, meaningful commit messages explaining the "why" not just the "what"
- Use branches for all feature development and bugfixes
- Keep commits focused and atomic

### Pull Request Protocol

- **Required Information**:
  - Clear description of changes made
  - Reference to related issues using `Closes #123` or `Fixes #123`
  - Screenshots for UI/UX changes
  - Testing steps and validation performed
  - Documentation updates if applicable

- **Review Checklist**:
  - [ ] Code follows existing style conventions
  - [ ] All tests pass and new functionality is tested
  - [ ] Documentation updated for user-facing changes
  - [ ] No API keys or sensitive data committed
  - [ ] Alfred workflow compliance verified
  - [ ] Performance impact considered

### Code Quality Standards

#### Python Style
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Document complex functions with docstrings
- Use meaningful variable and function names
- Implement proper error handling and logging

#### Alfred Integration
- Follow Alfred Script Filter JSON schema exactly
- Use appropriate Alfred environment variables
- Implement proper modifier key actions (⌥, ⌘, ⌃)
- Provide clear subtitles and action descriptions

#### Security Requirements
- Never commit API keys or credentials
- Use parameterised database queries to prevent injection
- Validate all user inputs and file paths
- Handle file operations safely with proper error checking

## Development Workflow

### Setting Up Development Environment

1. **Clone Repository**:
   ```bash
   git clone https://github.com/username/aifred.git
   cd aifred
   ```

2. **Install Dependencies**:
   ```bash
   python3 setup.py
   ```

3. **Configure Alfred**:
   - Import workflow into Alfred
   - Set environment variables for API keys
   - Test basic functionality

### Testing Your Changes

#### Manual Testing
- Test each Python module independently: `python3 aifred.py search test`
- Verify Alfred Script Filter output: `python3 alfred_filter.py "test query"`
- Test action handling: `python3 alfred_action.py "test_action"`
- Import real data files to verify parsing accuracy

#### Integration Testing
- Test within Alfred environment with real data
- Verify modifier key actions work correctly
- Test error scenarios and edge cases
- Validate API integrations with proper credentials

### Submitting Changes

1. **Create Feature Branch**: `git checkout -b feature/conversation-export`
2. **Make Focused Commits**: Each commit should represent a single logical change
3. **Update Documentation**: Include relevant README and code comment updates
4. **Test Thoroughly**: Verify your changes don't break existing functionality
5. **Create Pull Request**: Use the PR template and fill out all required sections

## Issue Reporting Guidelines

When reporting bugs or requesting features, please include:

### Bug Reports
- **Environment**: macOS version, Alfred version, Python version
- **Steps to Reproduce**: Detailed steps that consistently reproduce the issue
- **Expected Behaviour**: What should happen
- **Actual Behaviour**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Sample Data**: Anonymised sample data if relevant to the bug

### Feature Requests
- **Use Case**: Describe the problem you're trying to solve
- **Proposed Solution**: Your suggested approach (optional)
- **Alternatives Considered**: Other solutions you've thought about
- **Additional Context**: Screenshots, mockups, or examples

## Code of Conduct

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and solutions
- Help newcomers get started with contributing
- Report inappropriate behaviour to project maintainers

## Getting Help

- **Documentation**: Start with `README.md` and `AGENTS.md`
- **Issues**: Search existing issues before creating new ones
- **Alfred Community**: The [Alfred Forum](https://www.alfredforum.com/) for workflow-specific questions
- **Development**: Create an issue for development-related questions

Thank you for contributing to Aifred! 🚀