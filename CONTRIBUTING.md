# Contributing to European Youth Portal Scraper

Thank you for considering contributing to the European Youth Portal Scraper! 🎉

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/europayouthscraper.git
   cd europayouthscraper
   ```

3. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Write descriptive docstrings for functions and classes
- Use meaningful variable and function names

### Testing
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

### Pre-commit Hooks
We use pre-commit hooks to ensure code quality:
```bash
pip install pre-commit
pre-commit install
```

## 📝 Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

### Commit Message Format
We follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## 🐛 Bug Reports

When filing a bug report, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages/logs

## 💡 Feature Requests

For feature requests, please include:
- Use case description
- Expected functionality
- Any alternative solutions considered

## 📚 Areas for Contribution

- **Performance improvements** - Async optimization, rate limiting
- **Data analysis features** - New analytics and visualizations
- **Export formats** - Additional data export options
- **Documentation** - Tutorials, examples, API docs
- **Testing** - Unit tests, integration tests
- **Localization** - Multi-language support

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on collaboration

## 📞 Questions?

- Open an issue for questions
- Check existing issues first
- Join discussions in issue comments

Thank you for contributing! 🙏 