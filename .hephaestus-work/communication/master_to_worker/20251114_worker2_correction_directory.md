# Correction: Directory Structure

**Task ID**: phase1_task2_persistence_layer_correction
**Priority**: high
**Assigned to**: worker-2
**Timestamp**: 2025-11-14T17:24:00+09:00

## Issue

You are currently creating files in `src/persistence/`, but according to the design document (section 4.2), all code should be under `hermes_cli/` directory structure.

## Required Action

**IMPORTANT**: Please move/recreate all persistence layer files from `src/persistence/` to `hermes_cli/persistence/`.

### Correct Path Structure

```
/home/ubuntu/python_project/Hermes/
└── hermes_cli/
    └── persistence/
        ├── __init__.py
        ├── file_paths.py
        ├── config_repository.py
        ├── task_repository.py
        ├── history_repository.py
        └── log_repository.py
```

### Steps

1. Move existing files from `src/persistence/` to `hermes_cli/persistence/`
2. Continue implementation in `hermes_cli/persistence/`
3. Remove or ignore `src/` directory

## Design Reference

See section 4.2 of `/home/ubuntu/python_project/Hermes/詳細設計書.md`:

```
hermes/
├── hermes_cli/
│   ├── persistence/
```

The `hermes_cli/` directory has already been created by worker-1/3.

## Apologies

This should have been clarified in the original task assignment. Thank you for your attention to detail in noticing this discrepancy.
