# 🤝 Contributing Guide

Thank you for your interest in contributing to AutoDesk Kiwi! Here's how you can help make this project better.

---

## 📋 How to Contribute

### 1. Fork and Clone

```bash
# Fork the project on GitHub, then:
git clone https://github.com/YOUR_USERNAME/autodesk_kiwi.git
cd autodesk_kiwi
```

### 2. Create a Branch

```bash
git checkout -b feature/my-awesome-feature
```

### 3. Set Up the Environment

```bash
# Backend setup
cd api
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your values
```

### 4. Make Your Changes

- Follow the existing code style
- Add tests when possible
- Comment complex code sections
- Write clear, descriptive commit messages
- Keep changes focused and atomic

### 5. Test Your Changes

```bash
# Start the API server
cd api
uvicorn main:app --reload

# Open web/index.html in your browser
# Test all affected features thoroughly
```

### 6. Commit and Push

```bash
git add .
git commit -m "feat: add amazing feature description"
git push origin feature/my-awesome-feature
```

### 7. Create a Pull Request

Go to GitHub and create a Pull Request targeting the `main` branch.

**In your PR description, please include:**
- What changes you made
- Why these changes are needed
- Screenshots (if UI changes)
- Any breaking changes

---

## 📝 Code Standards

### Python (Backend)

- **Version**: Python 3.12+
- **Type Hints**: Use type hints everywhere
- **Docstrings**: Add docstrings for public functions and classes
- **Logging**: Use `logger` instead of `print()` statements
- **Style Guide**: Follow [PEP 8](https://peps.python.org/pep-0008/)
- **Imports**: Group imports (standard library, third-party, local)
- **Error Handling**: Use specific exceptions, not bare `except:`

**Example:**
```python
from typing import Optional
from logger import setup_logger

logger = setup_logger("module_name")

def fetch_data(user_id: int) -> Optional[dict]:
    """
    Fetch user data by ID.

    Args:
        user_id: The unique identifier for the user

    Returns:
        User data dictionary or None if not found
    """
    try:
        # Implementation here
        logger.info(f"Fetching data for user {user_id}")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch user data: {e}")
        raise
```

### JavaScript (Frontend)

- **Code Style**: Clean, readable, and well-commented
- **Avoid Globals**: Minimize global scope pollution
- **Browser Testing**: Test on Chrome, Firefox, Safari, Edge
- **Alpine.js**: Follow Alpine.js best practices
- **ES6+**: Use modern JavaScript features

**Example:**
```javascript
// Good: Clear function with descriptive name
async loadTasks() {
  try {
    const tasks = await this.fetchJSON(`${this.API_BASE}/tasks`);
    this.tasks = tasks;
  } catch (error) {
    this.showToast('Failed to load tasks', 'error');
  }
}
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: add dark mode toggle to settings
fix: resolve timezone issue in Hyperplanning parser
docs: update installation instructions for Windows
refactor: improve error handling in API client
test: add unit tests for task filtering
```

---

## 🐛 Reporting Bugs

Found a bug? Please open an issue with the following information:

### Required Information

- **Clear Title**: Summarize the issue in one line
- **Description**: Detailed explanation of the problem
- **Steps to Reproduce**:
  1. Go to '...'
  2. Click on '...'
  3. See error
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable, add screenshots
- **Environment**:
  - OS: [e.g., Windows 11, macOS 13.5, Ubuntu 22.04]
  - Python Version: [e.g., 3.12.1]
  - Browser: [e.g., Chrome 120, Firefox 121]

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior.

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.12.1]
- Browser: [e.g., Chrome 120]

**Additional context**
Any other relevant information.
```

---

## 💡 Suggesting Features

Have an idea for a new feature? We'd love to hear it!

### Feature Request Guidelines

Open an issue with:

- **Clear Title**: Feature name or summary
- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Use Cases**: Real-world scenarios where this helps
- **Mockups/Examples**: UI mockups or code examples (if applicable)
- **Alternatives**: Other solutions you've considered

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature.

**Problem It Solves**
What problem does this feature address?

**Proposed Solution**
How should this feature work?

**Use Cases**
Specific scenarios where this feature is useful.

**Mockups/Examples**
Visual mockups or code examples (optional).

**Alternatives Considered**
Other approaches you've thought about.
```

---

## ✅ Pull Request Checklist

Before submitting your PR, ensure:

- [ ] **Code Works**: Tested locally and works as expected
- [ ] **No Secrets**: No API keys, tokens, or sensitive data in code
- [ ] **Clean Commits**: Clear, descriptive commit messages
- [ ] **Documentation**: Updated README, docs, or code comments if needed
- [ ] **Code Quality**: Follows project coding standards
- [ ] **No Breaking Changes**: Or clearly documented if unavoidable
- [ ] **Tests Pass**: All existing tests still pass
- [ ] **Linting**: Code passes linting (if linter is configured)

---

## 🎨 Development Tips

### Useful Commands

```bash
# Run the backend with auto-reload
cd api
uvicorn main:app --reload --port 8000

# View API documentation
# Visit http://127.0.0.1:8000/docs

# Format Python code (if black is installed)
black api/

# Type checking (if mypy is installed)
mypy api/

# Run tests (if pytest is configured)
pytest
```

### Project Structure Tips

- **Backend**: All backend code in `api/` directory
- **Frontend**: All frontend code in `web/` directory
- **Routes**: Add new API endpoints in `api/routes/`
- **Models**: Add new data models in `api/models.py`
- **Documentation**: Add docs in `docs/` directory

---

## 📚 Resources

### Official Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [Alpine.js Guide](https://alpinejs.dev/) - Frontend framework
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) - ORM
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation

### Style Guides

- [PEP 8](https://peps.python.org/pep-0008/) - Python style guide
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Learning Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Alpine.js Examples](https://alpinejs.dev/examples)
- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

---

## 🌟 Recognition

Contributors will be recognized in:
- GitHub Contributors list
- Project acknowledgments
- Release notes (for significant contributions)

---

## 🙏 Thank You!

Every contribution, big or small, is greatly appreciated! Whether you're fixing a typo, reporting a bug, or adding a major feature, you're helping make AutoDesk Kiwi better for everyone.

**Happy Coding!** 🚀

---

## ❓ Questions?

If you have questions about contributing:
1. Check existing [Issues](https://github.com/Kiwi6212/autodesk_kiwi/issues)
2. Open a new [Discussion](https://github.com/Kiwi6212/autodesk_kiwi/discussions)
3. Reach out to maintainers

We're here to help! 😊
