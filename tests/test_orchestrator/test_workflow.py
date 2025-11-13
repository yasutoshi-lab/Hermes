"""Tests for orchestrator workflow wiring and helpers."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config import settings  # noqa: E402
from orchestrator.workflow import (  # noqa: E402
    WorkflowDependencies,
    WorkflowRunResult,
    compile_workflow,
    run_workflow,
    should_continue_verification,
)
from state.agent_state import create_initial_state  # noqa: E402


def _stub_node(name, payload=None, call_log=None):
    payload = payload or {}

    def _runner(state):
        if call_log is not None:
            call_log.append(name)
        return dict(payload)

    return _runner


class TestWorkflow(unittest.TestCase):
    """Verify dependency injection and streaming behavior."""

    def test_dependency_overrides_are_respected(self):
        calls = []
        deps = WorkflowDependencies(
            input_node=_stub_node("input", {"messages": []}, calls),
            search_node=_stub_node("search", {"search_results": []}, calls),
            processing_node=_stub_node("processing", {"processed_data": []}, calls),
            llm_node=_stub_node("llm", {"provisional_answer": "draft"}, calls),
            verification_node=_stub_node(
                "verification",
                {"verification_summary": {"needs_additional_search": False}},
                calls,
            ),
            report_node=_stub_node(
                "report",
                {"final_report": "ok", "report_path": "/tmp/report.md"},
                calls,
            ),
        )
        app = compile_workflow(dependencies=deps)
        initial_state = create_initial_state(query="test", language="en")
        initial_state["messages"] = [{"role": "user", "content": "test"}]  # type: ignore[index]

        result = app.invoke(initial_state, {"configurable": {"thread_id": "unittest"}})
        self.assertEqual(result["final_report"], "ok")
        self.assertEqual(
            calls,
            ["input", "search", "processing", "llm", "verification", "report"],
        )

    def test_run_workflow_stream_returns_events(self):
        deps = WorkflowDependencies(
            input_node=_stub_node("input", {"messages": []}),
            search_node=_stub_node("search", {"search_results": []}),
            processing_node=_stub_node("processing", {"processed_data": []}),
            llm_node=_stub_node("llm", {"provisional_answer": "draft"}),
            verification_node=_stub_node(
                "verification",
                {"verification_summary": {"needs_additional_search": False}},
            ),
            report_node=_stub_node("report", {"final_report": "done"}),
        )
        result = run_workflow(
            query="stream test",
            language="en",
            stream=True,
            dependencies=deps,
        )
        self.assertIsInstance(result, WorkflowRunResult)
        self.assertEqual(result.final_state["final_report"], "done")
        self.assertEqual(
            [event.node for event in result.events],
            ["input_node", "search_node", "processing_node", "llm_node", "verification_node", "report_node"],
        )

    def test_should_continue_verification_respects_summary(self):
        state = create_initial_state(query="q", language="en")
        state["verification_summary"] = {
            "needs_additional_search": True,
            "pass_ratio": 0.5,
            "average_confidence": 0.3,
        }  # type: ignore[index]
        decision = should_continue_verification(state)
        self.assertEqual(decision, "search_node")

        state["verification_summary"] = {
            "needs_additional_search": False,
            "pass_ratio": 0.95,
            "average_confidence": 0.9,
        }  # type: ignore[index]
        state["verification_count"] = settings.verification_max_loops  # type: ignore[index]
        decision = should_continue_verification(state)
        self.assertEqual(decision, "report_node")


if __name__ == "__main__":
    unittest.main()
