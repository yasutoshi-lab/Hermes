"""LangGraph workflow definition for Hermes.

This module defines the complete workflow graph for the Hermes research agent,
orchestrating all nodes from prompt normalization through final report generation.
"""

from langgraph.graph import Graph, END
from hermes_cli.agents.state import HermesState
from hermes_cli.agents.nodes import (
    prompt_normalizer,
    query_generator,
    web_researcher,
    container_processor,
    draft_aggregator,
    validation_controller,
    validator,
    final_reporter,
)
import logging

logger = logging.getLogger(__name__)


def should_continue_validation(state: HermesState) -> str:
    """Routing function for validation loop.

    Determines whether to continue validation or proceed to final report
    based on the validation_complete flag.

    Args:
        state: Current workflow state

    Returns:
        Next node name: "validator" or "final_reporter"
    """
    if state.validation_complete:
        return "final_reporter"
    else:
        return "validator"


def create_hermes_workflow() -> Graph:
    """Create and configure the Hermes workflow graph.

    Builds the complete LangGraph workflow with all nodes and edges,
    including the validation loop logic.

    Returns:
        Configured and compiled LangGraph workflow

    Workflow structure:
        prompt_normalizer → query_generator → web_researcher →
        container_processor → draft_aggregator → validation_controller ──┐
                                                 ├─ continue → validator ──┘ (loop)
                                                 └─ complete → final_reporter → END
    """
    logger.info("Creating Hermes workflow graph")

    # Create graph
    workflow = Graph()

    # Add nodes
    workflow.add_node("prompt_normalizer", prompt_normalizer)
    workflow.add_node("query_generator", query_generator)
    workflow.add_node("web_researcher", web_researcher)
    workflow.add_node("container_processor", container_processor)
    workflow.add_node("draft_aggregator", draft_aggregator)
    workflow.add_node("validation_controller", validation_controller)
    workflow.add_node("validator", validator)
    workflow.add_node("final_reporter", final_reporter)

    # Define edges (workflow sequence)
    workflow.set_entry_point("prompt_normalizer")

    workflow.add_edge("prompt_normalizer", "query_generator")
    workflow.add_edge("query_generator", "web_researcher")
    workflow.add_edge("web_researcher", "container_processor")
    workflow.add_edge("container_processor", "draft_aggregator")
    workflow.add_edge("draft_aggregator", "validation_controller")

    # Conditional edge for validation loop
    workflow.add_conditional_edges(
        "validation_controller",
        should_continue_validation,
        {
            "validator": "validator",
            "final_reporter": "final_reporter",
        }
    )

    # Validation loop back to aggregator
    workflow.add_edge("validator", "draft_aggregator")

    # End after final report
    workflow.add_edge("final_reporter", END)

    logger.info("Workflow graph created successfully")
    return workflow.compile()
