"""CLI tests covering query/history/model commands."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import importlib

cli_main_module = importlib.import_module("cli.main")  # noqa: E402
from cli.main import cli  # noqa: E402
from orchestrator.workflow import WorkflowEvent, WorkflowRunResult  # noqa: E402


def test_query_command_runs_workflow_and_writes_output(tmp_path):
    runner = CliRunner()
    output_path = tmp_path / "report.md"
    final_state = {"final_report": "hello", "report_path": "sessions/session_1/report.md"}

    with patch.object(cli_main_module, "run_workflow", return_value=final_state) as mock_run:
        result = runner.invoke(cli, ["query", "test query", "--output", str(output_path)])

    assert result.exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "hello"
    mock_run.assert_called_once()


def test_query_command_verbose_streams_events():
    runner = CliRunner()
    events = [
        WorkflowEvent(node="input_node", payload={"messages": []}),
        WorkflowEvent(node="report_node", payload={"final_report": "ok"}),
    ]
    result_bundle = WorkflowRunResult(final_state={"final_report": "ok"}, events=events)

    with patch.object(cli_main_module, "run_workflow", return_value=result_bundle):
        result = runner.invoke(cli, ["query", "stream me", "--verbose"])

    assert result.exit_code == 0
    assert "input_node" in result.output
    assert "report_node" in result.output


def test_history_list_uses_history_manager():
    runner = CliRunner()
    fake_manager = MagicMock()
    fake_manager.list_sessions.return_value = ["session_a", "session_b"]

    with patch.object(cli_main_module, "_get_history_manager", return_value=fake_manager):
        result = runner.invoke(cli, ["history", "list", "--limit", "1"])

    assert result.exit_code == 0
    fake_manager.list_sessions.assert_called_once()
    assert "session_a" in result.output


def test_models_list_handles_manager_errors(monkeypatch):
    runner = CliRunner()

    def fake_manager():
        raise click.ClickException("ollama missing")

    with patch.object(cli_main_module, "_get_model_manager", side_effect=fake_manager):
        result = runner.invoke(cli, ["models", "list"])

    assert result.exit_code != 0
    assert "ollama missing" in result.output
