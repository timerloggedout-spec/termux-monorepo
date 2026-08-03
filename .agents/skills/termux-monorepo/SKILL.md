```markdown
# termux-monorepo Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches best practices and conventions for contributing to the `termux-monorepo` Python repository. You'll learn about file naming, import/export styles, commit message conventions, and how to structure and run tests. While no specific frameworks or automated workflows are detected, this guide will help you maintain consistency and quality in your contributions.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `my_module.py`, `data_processor.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import helper_function
    ```

### Export Style
- Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    __all__ = ['MyClass', 'my_function']
    ```

### Commit Messages
- Follow **conventional commit** style.
- Use the `feat` prefix for new features.
- Keep commit messages concise (average ~76 characters).
  - Example:
    ```
    feat: add support for custom configuration files
    ```

## Workflows

### Adding a New Feature
**Trigger:** When you want to introduce a new feature to the codebase  
**Command:** `/add-feature`

1. Create a new branch for your feature.
2. Implement your feature in a new or existing snake_case Python file.
3. Use relative imports as needed.
4. Add or update named exports with `__all__`.
5. Write corresponding tests in a `*.test.*` file.
6. Commit your changes using the `feat` prefix.
7. Open a pull request for review.

### Running Tests
**Trigger:** When you need to verify your code changes  
**Command:** `/run-tests`

1. Locate all test files matching the `*.test.*` pattern.
2. Run the tests using your preferred Python test runner (e.g., `pytest` or `unittest`).
   - Example:
     ```
     python -m unittest discover -s . -p "*.test.*"
     ```
3. Review test results and fix any failures before committing.

## Testing Patterns

- Test files follow the `*.test.*` naming convention.
  - Example: `utils.test.py`, `data_processor.test.py`
- The specific test framework is not specified; use standard Python testing tools like `unittest` or `pytest`.
- Place tests alongside the modules they test or in a dedicated test directory.

**Example test file:**
```python
import unittest
from .utils import helper_function

class TestHelperFunction(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(helper_function(2), 4)
```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /add-feature   | Start the workflow for adding a new feature  |
| /run-tests     | Run all tests in the repository              |
```
