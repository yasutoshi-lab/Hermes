# `hermes task` Command

The `hermes task` command is used to manage research tasks (add, list, delete).

## Functionality

This command persists research prompts as tasks to be executed later with `hermes run`.

-   **Add Task**: Registers a new research prompt as a task. The task is assigned a unique ID.
-   **List Tasks**: Displays all currently registered tasks in a table format, along with their ID, status, prompt, and creation date.
-   **Remove Task**: Deletes the task with the specified task ID.

## Options

| Option | Description |
| :--- | :--- |
| `--add "PROMPT"` | Creates a new task with the specified prompt. |
| `--list` | Lists all registered tasks. |
| `--remove "TASK_ID"` | Deletes the task with the specified task ID. |
| `--work-dir PATH` | Specifies the path to the working directory. The default is `~/.hermes`. |

## Implementation Details

-   **CLI Framework**: `click`
-   **Service**: `hermes_cli.services.task_service.TaskService`
-   **Main Logic**:
    1.  Initializes the `TaskService`. This service is responsible for the persistence of tasks (reading and writing files).
    2.  If the `--add` option is specified:
        -   Calls `TaskService.create_task()` to create a new task file containing the prompt.
        -   Displays the ID and prompt of the created task.
    3.  If the `--list` option is specified:
        -   Calls `TaskService.list_tasks()` to read all task files in the working directory.
        -   Uses `rich.table.Table` to display the list of tasks in a formatted table.
    4.  If the `--remove` option is specified:
        -   Calls `TaskService.delete_task()` to delete the task file corresponding to the specified ID.
    5.  If none of the options are specified, it displays a message on how to use the command.
