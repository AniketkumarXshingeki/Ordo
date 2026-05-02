# Contributing to Ordo

Thank you for your interest in contributing to Ordo! We welcome contributions from the community.

## Development Setup

### Prerequisites
- Python 3.13 or higher
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd ordo

# Install dependencies
pip install -e .

# Run tests (if available)
# pytest
```

## How to Contribute

### 1. Reporting Issues
- Use the GitHub issue tracker
- Provide detailed steps to reproduce
- Include your environment (OS, Python version, etc.)

### 2. Feature Requests
- Check if the feature is already planned
- Provide use case and rationale
- Consider implementation complexity

### 3. Code Contributions

#### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Write tests if applicable
5. Ensure all tests pass
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Create a Pull Request

#### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

#### Testing
- Write unit tests for new features
- Test on multiple platforms if possible
- Include integration tests for CLI commands

### 4. Documentation
- Update README.md for new features
- Add docstrings to new functions
- Update existing documentation

## Project Structure

```
ordo/
├── agent/           # AI agent and NLP
├── indexer/         # File indexing and search
├── memory/          # Context management
├── models/          # Data models
├── safety/          # Security and validation
├── tools/           # Core functionality
├── utils/           # Utilities
└── app.py           # Main CLI application
```

## Guidelines

### Commit Messages
- Use clear, descriptive messages
- Start with verb (Add, Fix, Update, etc.)
- Reference issue numbers when applicable

### Pull Requests
- Provide clear description of changes
- Reference related issues
- Include screenshots for UI changes
- Ensure CI passes

### Code Review
- Be respectful and constructive
- Explain reasoning for suggestions
- Focus on code quality and maintainability

## Areas for Contribution

### High Priority
- Performance optimizations
- Cross-platform compatibility
- Additional file type support
- Enhanced AI capabilities

### Medium Priority
- GUI improvements
- Plugin system
- Cloud storage integration
- Mobile app

### Low Priority
- Internationalization
- Theming
- Advanced analytics

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## Contact

- GitHub Issues: For bugs and feature requests
- GitHub Discussions: For questions and general discussion

Thank you for contributing to Ordo! 🚀