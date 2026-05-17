# Contributing Guidelines (CONTRIBUTING)

Welcome to the project! We appreciate your interest in contributing. To make the development process smooth and effective, please follow these guidelines.

## 1. Environment Setup

This project requires **Python 3.12**.

1. **Clone the repository.**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate it:**
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. **Install the project in editable mode** with all development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## 2. Code Style and Tools

We use **Ruff** for linting and code formatting. All rules are configured in `pyproject.toml`.

- **Check for errors:** `ruff check .`
- **Format code automatically:** `ruff format .`

**Important:** Before creating a Pull Request, ensure that `ruff check` passes without any errors.

## 3. Commit Standards

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard. Every commit message must start with a type:

- `feat:` — new functionality.
- `fix:` — bug fixes.
- `docs:` — changes in documentation.
- `build:` — changes to `pyproject.toml` or dependencies.
- `refactor:` — code changes that neither fix a bug nor add a feature.
- `chore:` — maintenance tasks (creating folders, config files, etc.).

**Example:** `feat(ui): add keybinding for month view switch`

## 4. Workflow

1. **Pick an Issue** on GitHub.
2. **Create a new branch** from `main` with a descriptive name:
   - `feature/issue-id-description`
   - `fix/issue-id-description`
3. **Write your code**, following the [Data Specification](docs/data_spec.md).
4. **Run tests** (if any): `pytest`.
5. **Create a Pull Request (PR)**. In the PR description, include `Closes #Issue_ID`.

## 5. Project Structure

We use the `src` layout:
- `src/tui_calendar/ui/` — everything related to rendering (Textual).
- `src/tui_calendar/core/` — logic, parsing, and file management.
- `tests/` — unit tests.
- `examples/` — sample Markdown files for debugging and testing.

## 6. Communication

If you have questions regarding the implementation:
1. **Leave a comment** in the corresponding Issue.
2. If you need to suggest changes to the **MVP** or **Data Specification**, start a new **Discussion** on GitHub.
