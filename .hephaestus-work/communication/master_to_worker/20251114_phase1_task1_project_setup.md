# Task: Project Structure and Dependencies Setup

**Task ID**: phase1_task1_project_setup
**Priority**: high
**Assigned to**: worker-1
**Dependencies**: None

## Objective
Set up the foundational project structure, dependency management files, and directory skeleton for the Hermes CLI application.

## Context
This is the initial setup task for the Hermes project - a CLI-based information gathering agent. The project uses Python 3.10+, LangGraph for workflow management, browser-use for web automation, and Ollama for LLM integration.

Project root: `/home/ubuntu/python_project/Hermes/`

## Requirements

### 1. Create pyproject.toml
- Project name: `hermes-cli`
- Version: `1.0.0`
- Python requirement: `>=3.10`
- Dependencies:
  - typer
  - httpx
  - langgraph
  - pydantic
  - browser-use
  - dagger-io
  - pyyaml
  - rich
  - watchdog
- Entry point: `hermes = hermes_cli.main:app`

### 2. Create requirements.txt
Include all dependencies listed above with flexible version constraints.

### 3. Create Directory Structure
```
/home/ubuntu/python_project/Hermes/
├── hermes_cli/
│   ├── __init__.py
│   ├── main.py (placeholder)
│   ├── commands/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── nodes/
│   │       └── __init__.py
│   ├── tools/
│   │   └── __init__.py
│   └── persistence/
│       └── __init__.py
├── pyproject.toml
└── requirements.txt
```

### 4. Create __init__.py Files
- Each `__init__.py` should contain proper module docstrings
- Main `hermes_cli/__init__.py` should include version info: `__version__ = "1.0.0"`

### 5. Create main.py Placeholder
- Import typer
- Create basic `app = typer.Typer()` instance
- Add placeholder `def main():` function
- Add if `__name__ == "__main__":` block

## Expected Output

1. All directory structure created at `/home/ubuntu/python_project/Hermes/`
2. `pyproject.toml` with complete configuration
3. `requirements.txt` with all dependencies
4. All `__init__.py` files with proper docstrings
5. `main.py` placeholder ready for command registration

## Resources

- Design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (sections 3, 4)
- Python packaging docs: https://packaging.python.org/
- Typer documentation: https://typer.tiangolo.com/

## Success Criteria

- All directories and files created successfully
- No import errors when running `python -c "import hermes_cli"`
- Project structure matches design specification section 4.2
