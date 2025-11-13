"""
LangGraph Workflow for the Hermes Research Analyst Agent.

This module wires the production node implementations into a StateGraph and
exposes helper APIs for CLI/integration layers. It supports dependency injection
so tests and alternative frontends can override node behavior or provide custom
clients (Search, Container, Model, etc.) without patching global modules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from config import settings
from nodes.input_node import input_node as default_input_node
from nodes.search_node import search_node as default_search_node
from nodes.processing_node import processing_node as default_processing_node
from nodes.llm_node import llm_node as default_llm_node
from nodes.verification_node import verification_node as default_verification_node
from nodes.report_node import report_node as default_report_node
from state.agent_state import AgentState, NodeFunction, create_initial_state

logger = logging.getLogger(__name__)


@dataclass
class WorkflowEvent:
    """Lightweight structure describing node-level updates emitted by the graph."""

    node: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkflowRunResult:
    """Return type when `run_workflow` is executed in streaming mode."""

    final_state: AgentState
    events: List[WorkflowEvent]


@dataclass
class WorkflowDependencies:
    """
    Optional dependency overrides for the workflow.

    Attributes:
        input_node: Custom input node callable
        search_node: Custom search node callable
        processing_node: Custom processing node callable
        llm_node: Custom llm node callable
        verification_node: Custom verification node callable
        report_node: Custom report node callable
        search_client: Shared WebSearchClient instance injected into SearchNode
        container_processor: ContainerProcessor injected into ProcessingNode
        history_manager: HistoryManager shared across nodes that persist history
        model_manager: ModelManager shared with LLM node (set on state)
        on_event: Callback fired after each node execution with WorkflowEvent payload
    """

    input_node: Optional[NodeFunction] = None
    search_node: Optional[NodeFunction] = None
    processing_node: Optional[NodeFunction] = None
    llm_node: Optional[NodeFunction] = None
    verification_node: Optional[NodeFunction] = None
    report_node: Optional[NodeFunction] = None
    search_client: Optional[Any] = None
    container_processor: Optional[Any] = None
    history_manager: Optional[Any] = None
    model_manager: Optional[Any] = None
    on_event: Optional[Callable[[WorkflowEvent], None]] = None


def _wrap_node_with_logging(
    name: str,
    fn: NodeFunction,
    event_hook: Optional[Callable[[WorkflowEvent], None]],
) -> NodeFunction:
    def wrapper(state: AgentState) -> Dict[str, Any]:
        logger.info("Workflow[%s]: start", name)
        result = fn(state)
        logger.info("Workflow[%s]: completed (keys=%s)", name, ", ".join(result.keys()))
        if event_hook:
            event_hook(WorkflowEvent(node=name, payload=result))
        return result

    return wrapper


def _inject_model_manager(fn: NodeFunction, manager: Any | None) -> NodeFunction:
    if manager is None:
        return fn

    def runner(state: AgentState) -> Dict[str, Any]:
        state["model_manager"] = manager  # type: ignore[index]
        return fn(state)

    return runner


def _build_node_registry(deps: WorkflowDependencies) -> Dict[str, NodeFunction]:
    registry: Dict[str, NodeFunction] = {
        "input_node": deps.input_node
        or partial(default_input_node, history_manager=deps.history_manager),
        "search_node": deps.search_node
        or partial(
            default_search_node,
            client=deps.search_client,
            history_manager=deps.history_manager,
        ),
        "processing_node": deps.processing_node
        or partial(
            default_processing_node,
            processor=deps.container_processor,
            history_manager=deps.history_manager,
        ),
        "llm_node": deps.llm_node
        or _inject_model_manager(default_llm_node, deps.model_manager),
        "verification_node": deps.verification_node or default_verification_node,
        "report_node": deps.report_node or default_report_node,
    }
    return registry


def should_continue_verification(state: AgentState) -> Literal["search_node", "report_node"]:
    """
    Decide whether another verification loop should trigger a re-search.

    Decision factors:
        - verification_summary.needs_additional_search (explicit signal)
        - pass ratio vs. settings.verification_pass_ratio
        - average confidence vs. settings.verification_min_confidence
        - maximum loop guard (settings.verification_max_loops)
    """
    verification_count = state.get("verification_count", 0)
    summary = state.get("verification_summary") or {}

    needs_additional = bool(summary.get("needs_additional_search"))
    status = summary.get("status") or state.get("verification_status")
    pass_ratio = summary.get("pass_ratio")
    avg_confidence = summary.get("average_confidence")

    should_retry = needs_additional or status in {"fail", "retry"}

    if pass_ratio is not None and pass_ratio < settings.verification_pass_ratio:
        should_retry = True

    if (
        avg_confidence is not None
        and avg_confidence < settings.verification_min_confidence
    ):
        should_retry = True

    if should_retry and verification_count < settings.verification_max_loops:
        return "search_node"

    return "report_node"


def create_workflow(
    dependencies: Optional[WorkflowDependencies] = None,
) -> StateGraph:
    """
    Build the LangGraph workflow with optional dependency overrides.
    """
    deps = dependencies or WorkflowDependencies()
    workflow = StateGraph(AgentState)
    registry = _build_node_registry(deps)

    for name, fn in registry.items():
        workflow.add_node(name, _wrap_node_with_logging(name, fn, deps.on_event))

    workflow.add_edge("input_node", "search_node")
    workflow.add_edge("search_node", "processing_node")
    workflow.add_edge("processing_node", "llm_node")
    workflow.add_edge("llm_node", "verification_node")
    workflow.add_conditional_edges(
        "verification_node",
        should_continue_verification,
        {
            "search_node": "search_node",
            "report_node": "report_node",
        },
    )
    workflow.add_edge("report_node", END)
    workflow.set_entry_point("input_node")
    return workflow


def compile_workflow(
    dependencies: Optional[WorkflowDependencies] = None,
) -> StateGraph:
    """
    Compile the workflow with an in-memory checkpoint.
    """
    workflow = create_workflow(dependencies)
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


def visualize_workflow(
    output_path: str = "workflow_graph.png",
    dependencies: Optional[WorkflowDependencies] = None,
) -> None:
    """
    Create a PNG visualization of the workflow graph.
    """
    try:
        workflow = create_workflow(dependencies)
        graph = workflow.get_graph()
        png_data = graph.draw_mermaid_png()
        with open(output_path, "wb") as handle:
            handle.write(png_data)
        logger.info("Workflow visualization saved to %s", output_path)
    except ImportError:
        logger.warning("graphviz is not available. Skipping visualization.")
    except Exception as exc:
        logger.error("Failed to visualize workflow: %s", exc)


def _prepare_initial_state(
    query: Optional[str],
    messages: Optional[List[dict]],
    language: Optional[str],
    model_name: Optional[str],
    history_path: Optional[str],
    model_manager: Any | None,
) -> AgentState:
    if not messages and not query:
        raise ValueError("Either 'query' or 'messages' must be supplied.")

    resolved_language = (language or settings.default_language).lower()
    resolved_model = (model_name or settings.default_model).strip() or settings.default_model
    resolved_query = (query or "").strip()

    computed_messages = messages or [{"role": "user", "content": resolved_query}]
    state: AgentState = create_initial_state(
        query=resolved_query,
        language=resolved_language,
        model_name=resolved_model,
        history_path=history_path or "",
    )
    state["messages"] = computed_messages  # type: ignore[index]

    if model_manager is not None:
        state["model_manager"] = model_manager  # type: ignore[index]

    return state


def run_workflow(
    query: Optional[str] = None,
    *,
    messages: Optional[List[dict]] = None,
    language: Optional[str] = None,
    model_name: Optional[str] = None,
    history_path: Optional[str] = None,
    stream: bool = False,
    dependencies: Optional[WorkflowDependencies] = None,
    thread_id: Optional[str] = None,
) -> AgentState | WorkflowRunResult:
    """
    Convenience helper for executing the workflow from CLI/tests.

    Args:
        query: User query when bypassing the InputNode message extraction.
        messages: LangChain-style message history; overrides query if provided.
        language: Preferred language (defaults to settings).
        model_name: Override for the LLM model.
        history_path: Existing session directory to reuse (optional).
        stream: When True, return WorkflowRunResult with node events.
        dependencies: Optional WorkflowDependencies for DI/mocking.
        thread_id: LangGraph thread identifier; auto-generated if omitted.
    """
    deps = dependencies or WorkflowDependencies()
    initial_state = _prepare_initial_state(
        query=query,
        messages=messages,
        language=language,
        model_name=model_name,
        history_path=history_path,
        model_manager=deps.model_manager,
    )

    compiled = compile_workflow(dependencies=deps)
    computed_thread_id = thread_id or initial_state.get("history_path") or f"run_{uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": str(computed_thread_id)}}

    if not stream:
        return compiled.invoke(initial_state, config)

    events: List[WorkflowEvent] = []
    current_state: AgentState = dict(initial_state)  # type: ignore[assignment]

    for chunk in compiled.stream(initial_state, config):
        if not chunk:
            continue
        node_name, update = next(iter(chunk.items()))
        if isinstance(update, dict):
            current_state.update(update)
        events.append(WorkflowEvent(node=node_name, payload=update))

    return WorkflowRunResult(final_state=current_state, events=events)


__all__ = [
    "WorkflowDependencies",
    "WorkflowEvent",
    "WorkflowRunResult",
    "create_workflow",
    "compile_workflow",
    "visualize_workflow",
    "run_workflow",
    "should_continue_verification",
]
