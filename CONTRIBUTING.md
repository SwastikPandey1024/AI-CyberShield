# 🤝 Contributing to AI CyberShield

First off, thank you for considering contributing! We welcome contributions from everyone, whether it's reporting a bug, discussing improvements, or submitting code.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branch Strategy](#branch-strategy)
- [Commit Conventions](#commit-conventions)
- [Code Style](#code-style)
- [Pull Request Workflow](#pull-request-workflow)
- [Issue Reporting](#issue-reporting)
- [Development Setup](#development-setup)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/AI-CyberShield.git
   ```
3. Set up the development environment as described in the [Development Guide](docs/development-guide.md).
4. Create a branch for your work (see [Branch Strategy](#branch-strategy)).
5. Make your changes following our [Code Style](#code-style).
6. Submit a pull request (see [Pull Request Workflow](#pull-request-workflow)).

---

## Branch Strategy

We use a simplified Git Flow approach:

| Branch Prefix | Purpose |
|---------------|---------|
| `main` | Production-ready code. Protected — no direct commits. |
| `develop` | Integration branch for features. |
| `feat/*` | New features (e.g., `feat/add-batch-prediction`) |
| `fix/*` | Bug fixes (e.g., `fix/nan-handling-preprocessing`) |
| `docs/*` | Documentation updates (e.g., `docs/update-readme`) |
| `refactor/*` | Code restructuring (e.g., `refactor/extract-service-layer`) |
| `test/*` | Test additions or fixes (e.g., `test/add-predict-unit-tests`) |
| `chore/*` | Maintenance tasks (e.g., `chore/update-dependencies`) |

### Branch Naming Rules

- Use lowercase kebab-case.
- Keep branch names descriptive but concise.
- Reference issue numbers when applicable (e.g., `feat/42-add-batch-prediction`).

---

## Commit Conventions

We enforce [Conventional Commits](https://www.conventionalcommits.org/) for all commits:

```
<type>(<scope>): <description>

[optional body]
[optional footer(s)]
```

### Types

| Type | Usage | Example |
|------|-------|---------|
| `feat` | New feature | `feat(api): add batch prediction endpoint` |
| `fix` | Bug fix | `fix(preprocessing): handle NaN in scaling` |
| `docs` | Documentation | `docs: update API examples` |
| `refactor` | Code change without feature/fix | `refactor(services): extract prediction logic` |
| `test` | Adding or fixing tests | `test: add unit tests for predictor` |
| `chore` | Maintenance, deps, CI | `chore: update ruff to 0.3.0` |
| `style` | Formatting only | `style: apply black formatting` |

### Guidelines

- Write commits in **imperative present tense** ("add feature" not "added feature")
- **Scope** should reference the module (e.g., `api`, `preprocessing`, `docs`)
- Keep the first line under **72 characters**
- Use the body to explain **what** and **why**, not **how**

---

## Code Style

We enforce strict code style through automated tooling:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | Line length 88, Python 3.12 |
| **Ruff** | Linting | Rules: E, F, I, W, UP, N, D |
| **isort** | Import ordering | Black-compatible profile |
| **mypy** | Static type checking | Strict mode |

### Before Submitting

Run the following commands and ensure they pass:

```bash
# Format code
black .

# Sort imports
isort .

# Lint check
ruff check .

# Type check
mypy backend/ ml/
```

Refer to our full [Coding Standards](docs/coding-standards.md) for detailed guidelines on:
- Type hints and docstrings
- Naming conventions
- Error handling patterns
- Module responsibilities

---

## Pull Request Workflow

### 1. Before You Start

- Search existing issues and PRs to avoid duplication.
- For significant changes, open an issue first to discuss.
- Ensure your branch is up to date with `develop`.

### 2. Create Your Pull Request

1. Push your branch to your fork.
2. Open a PR against the `develop` branch.
3. Fill out the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
4. Link any related issues.

### 3. PR Review Process

- Maintainers will review your code within 2–3 business days.
- Address review feedback with additional commits.
- Once approved, a maintainer will merge your PR.

### 4. PR Requirements

- ✅ All tests pass
- ✅ No linter errors or warnings
- ✅ Type hints present on all function signatures
- ✅ Google-style docstrings on public functions
- ✅ Test coverage for new code (≥ 85%)
- ✅ Documentation updated if applicable

---

## Issue Reporting

### Bug Reports

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- **Clear description** of the issue
- **Steps to reproduce** with minimal code or data
- **Expected vs. actual behavior**
- **Environment details** (OS, Python version, package versions)
- **Logs or error messages** (if applicable)

### Feature Requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- **Problem statement** — what need does this address?
- **Proposed solution** — how should it work?
- **Alternative approaches** you've considered
- **Target users** who would benefit

---

## Development Setup

For detailed setup instructions, see the [Development Guide](docs/development-guide.md).

Quick start:

```bash
# Clone and enter the project
git clone https://github.com/your-username/AI-CyberShield.git
cd AI-CyberShield

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
black . && isort . && ruff check . && mypy backend/ ml/
```

---

## Questions?

If you have questions, feel free to open a [Discussion](https://github.com/yourusername/AI-CyberShield/discussions) or reach out to the maintainers.

---

*Thank you for contributing to AI CyberShield! 🛡️*
