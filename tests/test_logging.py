#!/usr/bin/env python3
"""
LogRepository smoke test.

Writes a few log lines and prints the last entries using the repository.
"""

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.log_repository import LogRepository


def main() -> None:
    repo = LogRepository(FilePaths())
    for idx in range(3):
        repo.write_log(
            "INFO",
            "INTEGRATION",
            f"Sample log line {idx + 1}",
            task_id="int-logs",
            step=idx + 1,
        )

    tail_lines = repo.tail(lines=5)
    print("=== Tail Output ===")
    for line in tail_lines:
        print(line.strip())


if __name__ == "__main__":
    main()
