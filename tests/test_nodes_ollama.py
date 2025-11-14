from typing import List

from hermes_cli.agents.nodes import draft_aggregator, query_generator, validator
from hermes_cli.agents.state import HermesState
from hermes_cli.tools.ollama_client import OllamaConfig


class StubOllamaClient:
    def __init__(self, responses: List[str], recorder: List[List[dict]]):
        self._responses = responses
        self._recorder = recorder

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def chat(self, messages, stream=False):
        self._recorder.append(messages)
        if not self._responses:
            raise RuntimeError("No stub responses remaining")
        return self._responses.pop(0)


def _factory_builder(responses: List[str], recorder: List[List[dict]]):
    def _factory(config: OllamaConfig):
        return StubOllamaClient(responses, recorder)

    return _factory


def _base_state(**overrides) -> HermesState:
    return HermesState(
        user_prompt="Explain the state of quantum networking research",
        language="en",
        query_count=overrides.get("query_count", 3),
        queries=overrides.get("queries", []),
        query_results=overrides.get("query_results", {}),
        processed_notes=overrides.get("processed_notes", {}),
        draft_report=overrides.get("draft_report"),
        loop_count=overrides.get("loop_count", 0),
        ollama_config=OllamaConfig(
            api_base="http://localhost:11434/api/chat",
            model="gpt-oss:20b",
            retry=1,
            timeout_sec=60,
        ),
        ollama_client_factory=overrides.get("factory"),
    )


def test_query_generator_parses_numbered_output():
    responses = ["1. Q1 about quantum\n2) Q2 about photons\n- Q3 cross-domain"]
    recorder: List[List[dict]] = []
    state = _base_state(query_count=3, factory=_factory_builder(responses, recorder))

    result = query_generator(state)

    assert result.queries == [
        "Q1 about quantum",
        "Q2 about photons",
        "Q3 cross-domain",
    ]
    assert len(recorder) == 1
    assert recorder[0][0]["role"] == "system"


def test_draft_aggregator_updates_report():
    responses = ["# Draft\n\nContent"]
    recorder: List[List[dict]] = []
    state = _base_state(
        processed_notes={"Query 1": "Note A", "Query 2": "Note B"},
        factory=_factory_builder(responses, recorder),
    )

    result = draft_aggregator(state)

    assert result.draft_report == "# Draft\n\nContent"
    assert "Original question" in recorder[0][1]["content"]


def test_validator_improves_report_and_increments_loop():
    responses = ["Improved draft"]
    recorder: List[List[dict]] = []
    state = _base_state(
        draft_report="Initial draft",
        loop_count=0,
        factory=_factory_builder(responses, recorder),
    )

    result = validator(state)

    assert result.draft_report == "Improved draft"
    assert result.loop_count == 1
    assert len(recorder) == 1


def test_validator_parses_follow_up_queries_from_report():
    responses = [
        """# Report

## Analysis
- detail

### Follow-up Queries
- Investigate photonic switches
* Compare entanglement metrics
- Evaluate funding roadmaps

## Appendix
content
"""
    ]
    recorder: List[List[dict]] = []
    state = _base_state(
        draft_report="Initial draft",
        loop_count=0,
        factory=_factory_builder(responses, recorder),
    )

    result = validator(state)

    assert result.loop_count == 1
    assert result.follow_up_queries == [
        "Investigate photonic switches",
        "Compare entanglement metrics",
        "Evaluate funding roadmaps",
    ]


def test_validator_falls_back_when_no_follow_up_section():
    responses = ["## Report body\nContent without follow ups"]
    recorder: List[List[dict]] = []
    state = _base_state(
        draft_report="Initial draft",
        loop_count=0,
        factory=_factory_builder(responses, recorder),
        queries=["Photonics outlook"],
        query_results={"Photonics outlook": []},
    )

    result = validator(state)

    assert result.follow_up_queries
    assert result.follow_up_queries[0].startswith("Photonics outlook")
