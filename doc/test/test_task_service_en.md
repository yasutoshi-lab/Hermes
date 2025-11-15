# `test_task_service.py`

This file contains unit tests for `hermes_cli.services.task_service.TaskService`.

## Objective

To verify that the CRUD (Create, Read, Update, Delete) operations for tasks handled by `TaskService` and their related business logic work correctly.

The dependency on `TaskRepository` (the persistence layer) is managed by using a temporary directory created with the `pytest` `tmp_path` fixture. This allows interaction with the actual file system while keeping the test execution environment clean.

## Test Case Overview

| Test Function | Description |
| :--- | :--- |
| `test_create_task` | Verifies that a new task is created correctly and its initial status is set to `scheduled`. |
| `test_get_task` | Verifies that a created task can be correctly retrieved by its ID. |
| `test_get_nonexistent_task` | Verifies that `None` is returned when trying to retrieve a task with a non-existent ID. |
| `test_list_tasks` | Verifies that all tasks can be retrieved in a list after multiple tasks have been created. |
| `test_list_tasks_by_status` | Verifies that the task list can be filtered by the `status` parameter. |
| `test_update_task_status` | Verifies that the status of a task (e.g., `scheduled` -> `running`) is updated correctly. |
| `test_delete_task` | Verifies that a specified task is deleted correctly and cannot be retrieved afterwards. |
| `test_update_nonexistent_task_status` | Verifies that no error occurs when trying to update the status of a non-existent task. |

## Fixture

| Fixture Name | Scope | Description |
| :--- | :--- | :--- |
| `task_service` | `function` | For each test function, it generates a new instance of `TaskService` with a temporary working directory (`tmp_path`). This prevents state interference between tests. |
