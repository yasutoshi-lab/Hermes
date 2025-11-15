# `hermes history` Command

The `hermes history` command is used to manage the history of tasks executed with `hermes run`.

## Functionality

This command operates on the execution results (metadata and reports) stored in the `history` directory of the workspace.

-   **List History**: Displays past execution history in a table format. It includes details such as Task ID, execution status (success/failure), execution time, model used, etc.
-   **Export Report**: Copies a previously generated report file to a specified path.
-   **Delete History**: Deletes the execution history (metadata and report file) for a specified task ID.

## Options

| Option | Description |
| :--- | :--- |
| `--limit INT` | Specifies the maximum number of history entries to display. |
| `--export "TASK_ID:PATH"` | Exports (copies) the report of the specified `TASK_ID` to the specified `PATH`. Delimited by a colon `:`. |
| `--delete "TASK_ID"` | Deletes the history for the specified `TASK_ID`. |
| `--work-dir PATH` | Specifies the path to the working directory. The default is `~/.hermes`. |

## Implementation Details

-   **CLI Framework**: `click`
-   **Service**: `hermes_cli.services.history_service.HistoryService`
-   **Main Logic**:
    1.  Initializes the `HistoryService`. This service is responsible for reading, writing, and deleting history files.
    2.  If the `--export` option is specified:
        -   Splits the argument into `TASK_ID` and `PATH`.
        -   Calls `HistoryService.export_report()` to copy the corresponding report file to the specified path.
    3.  If the `--delete` option is specified:
        -   Calls `HistoryService.delete_history()` to delete the metadata and report files corresponding to the specified ID.
    4.  If neither of the above options is specified (list view):
        -   Calls `HistoryService.list_histories()` to read all execution history metadata from the `history` directory.
        -   Uses `rich.table.Table` to display the list of histories in a formatted table. The status is also color-coded.
