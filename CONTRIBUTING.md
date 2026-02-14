# Contributing to Universal MCP Server

Thank you for your interest in contributing to the Universal MCP Server!

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

1. **Search existing issues** - Check if the bug has already been reported
2. **Create a new issue** - Use the bug report template
3. **Include details**:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version, OS, and relevant environment details

### Suggesting Features

1. **Search existing feature requests** - Avoid duplicates
2. **Use the feature request template**
3. **Explain clearly**:
   - What problem does this solve?
   - What would the solution look like?
   - Any alternative solutions considered?

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```
3. **Make your changes**
4. **Follow coding standards**:
   - Use meaningful variable names
   - Add docstrings to new functions
   - Keep functions focused and small
5. **Test your changes**:
   ```bash
   # Test the server
   python src/server.py
   ```
6. **Commit with clear messages**:
   ```bash
   git commit -m "Add amazing new feature"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/amazing-new-feature
   ```
8. **Submit a Pull Request**

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-server-demo.git
cd mcp-server-demo

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests (if available)
pytest
```

## Coding Standards

- **Python**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Type hints**: Use type hints where applicable
- **Docstrings**: Use Google-style docstrings
- **Line length**: Maximum 100 characters
- **Linting**: Run ruff before committing:
  ```bash
  ruff check src/
  ```

## Adding New Features

### Adding Tools

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int = 10) -> str:
    """Description for the AI model.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 10)
    
    Returns:
        JSON string with results
    """
    # Implementation
    return json.dumps({"result": "success"})
```

### Adding Resources

```python
@mcp.resource("custom://my-resource")
async def my_resource() -> str:
    """Description of what this resource provides."""
    return json.dumps({"data": "value"})
```

### Adding Prompts

```python
@mcp.prompt()
def my_prompt() -> str:
    """Instructions for the AI when using this prompt."""
    return """You are helping with..."""
```

## Questions?

- Open an issue for questions about contributing
- Join the MCP community Discord for discussions

## Recognition

Contributors will be recognized in the README and CHANGELOG.
