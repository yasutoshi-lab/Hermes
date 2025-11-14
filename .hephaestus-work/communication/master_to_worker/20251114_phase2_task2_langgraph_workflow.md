# Task: LangGraph Workflow Implementation

**Task ID**: phase2_task2_langgraph_workflow
**Priority**: high
**Assigned to**: worker-2
**Dependencies**: phase1_task3_tools_layer

## Objective
Implement the complete LangGraph-based agent workflow for Hermes, including state management, all workflow nodes, and the main graph orchestration.

## Context
LangGraph orchestrates the entire research workflow: query generation → web research → container processing → draft creation → validation loops → final report. This is the core intelligence of Hermes.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (sections 6.4, 9)

## Requirements

### 1. Implement `agents/state.py`

Define the state schema for the workflow:

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class HermesState(BaseModel):
    """State model for Hermes agent workflow."""

    # Input
    user_prompt: str = Field(description="Original user query/prompt")
    language: str = Field(default="ja", description="Output language (ja/en)")

    # Query generation
    queries: List[str] = Field(default_factory=list, description="Generated search queries")

    # Research results
    query_results: Dict[str, List[dict]] = Field(
        default_factory=dict,
        description="Search results per query: {query: [results]}"
    )

    # Processed data
    processed_notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Normalized text per query: {query: processed_text}"
    )

    # Report drafts
    draft_report: Optional[str] = Field(default=None, description="Current draft report")
    validated_report: Optional[str] = Field(default=None, description="Final validated report")

    # Validation control
    loop_count: int = Field(default=0, description="Current validation loop iteration")
    min_validation: int = Field(default=1, description="Minimum validation loops")
    max_validation: int = Field(default=3, description="Maximum validation loops")
    validation_complete: bool = Field(default=False, description="Validation completion flag")

    # Configuration
    min_sources: int = Field(default=3, description="Minimum sources per query")
    max_sources: int = Field(default=8, description="Maximum sources per query")

    # Metadata
    error_log: List[str] = Field(default_factory=list, description="Error messages")


    class Config:
        arbitrary_types_allowed = True
```

### 2. Implement Node Functions in `agents/nodes/`

Create individual node implementations:

#### `agents/nodes/__init__.py`
```python
"""Node implementations for Hermes workflow."""

from .prompt_normalizer import prompt_normalizer
from .query_generator import query_generator
from .web_researcher import web_researcher
from .container_processor import container_processor
from .draft_aggregator import draft_aggregator
from .validation_controller import validation_controller
from .validator import validator
from .final_reporter import final_reporter

__all__ = [
    "prompt_normalizer",
    "query_generator",
    "web_researcher",
    "container_processor",
    "draft_aggregator",
    "validation_controller",
    "validator",
    "final_reporter",
]
```

#### `agents/nodes/prompt_normalizer.py`
```python
from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def prompt_normalizer(state: HermesState) -> HermesState:
    """
    Normalize user prompt based on language setting.

    Args:
        state: Current workflow state

    Returns:
        Updated state with normalized prompt
    """
    logger.info(f"Normalizing prompt in language: {state.language}")

    # Basic normalization: strip whitespace, handle language-specific formatting
    normalized = state.user_prompt.strip()

    # Could add more sophisticated normalization here
    # For now, keep it simple

    logger.info("Prompt normalization complete")
    return state
```

#### `agents/nodes/query_generator.py`
```python
from hermes_cli.agents.state import HermesState
from hermes_cli.tools import OllamaClient, OllamaConfig
import logging

logger = logging.getLogger(__name__)


def query_generator(state: HermesState) -> HermesState:
    """
    Generate multiple search queries from user prompt using LLM.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated queries
    """
    logger.info("Generating search queries from prompt")

    # TODO: Get Ollama config from somewhere (will be provided by run_service)
    # For now, use placeholder

    prompt = f"""Based on the following research question, generate 3-5 diverse search queries
that would help gather comprehensive information.

Research Question: {state.user_prompt}

Language: {state.language}

Generate queries in {state.language}. Return only the queries, one per line."""

    try:
        # TODO: Implement actual LLM call
        # For now, create placeholder
        queries = [
            f"Query 1 for: {state.user_prompt}",
            f"Query 2 for: {state.user_prompt}",
            f"Query 3 for: {state.user_prompt}",
        ]

        state.queries = queries
        logger.info(f"Generated {len(queries)} queries")

    except Exception as e:
        logger.error(f"Query generation failed: {e}")
        state.error_log.append(f"Query generation error: {str(e)}")

    return state
```

#### `agents/nodes/web_researcher.py`
```python
from hermes_cli.agents.state import HermesState
from hermes_cli.tools import BrowserUseClient
import logging

logger = logging.getLogger(__name__)


def web_researcher(state: HermesState) -> HermesState:
    """
    Perform web research for each generated query.

    Args:
        state: Current workflow state

    Returns:
        Updated state with search results
    """
    logger.info(f"Starting web research for {len(state.queries)} queries")

    try:
        with BrowserUseClient(max_sources=state.max_sources) as browser:
            for idx, query in enumerate(state.queries):
                logger.info(f"Researching query {idx + 1}/{len(state.queries)}: {query}")

                try:
                    results = browser.search(query, max_sources=state.max_sources)
                    state.query_results[query] = [
                        {
                            "url": r.url,
                            "title": r.title,
                            "content": r.content,
                            "timestamp": r.timestamp,
                        }
                        for r in results
                    ]
                    logger.info(f"Found {len(results)} sources for query: {query}")

                except Exception as e:
                    logger.error(f"Failed to research query '{query}': {e}")
                    state.error_log.append(f"Research error for '{query}': {str(e)}")
                    state.query_results[query] = []

    except Exception as e:
        logger.error(f"Browser initialization failed: {e}")
        state.error_log.append(f"Browser error: {str(e)}")

    logger.info("Web research complete")
    return state
```

#### `agents/nodes/container_processor.py`
```python
from hermes_cli.agents.state import HermesState
from hermes_cli.tools import ContainerUseClient
import logging

logger = logging.getLogger(__name__)


def container_processor(state: HermesState) -> HermesState:
    """
    Process and normalize collected content in container environment.

    Args:
        state: Current workflow state

    Returns:
        Updated state with processed notes
    """
    logger.info("Processing content in container")

    try:
        with ContainerUseClient() as container:
            for query, results in state.query_results.items():
                if not results:
                    continue

                logger.info(f"Processing {len(results)} results for query: {query}")

                # Extract content from results
                texts = [r["content"] for r in results if r.get("content")]

                try:
                    # Normalize texts in container
                    normalized = container.normalize_texts(texts)

                    # Combine into single note
                    combined = "\n\n".join(normalized)
                    state.processed_notes[query] = combined

                    logger.info(f"Processed content for query: {query}")

                except Exception as e:
                    logger.error(f"Failed to process query '{query}': {e}")
                    state.error_log.append(f"Processing error for '{query}': {str(e)}")

    except Exception as e:
        logger.error(f"Container initialization failed: {e}")
        state.error_log.append(f"Container error: {str(e)}")

    logger.info("Container processing complete")
    return state
```

#### `agents/nodes/draft_aggregator.py`
```python
from hermes_cli.agents.state import HermesState
from hermes_cli.tools import OllamaClient
import logging

logger = logging.getLogger(__name__)


def draft_aggregator(state: HermesState) -> HermesState:
    """
    Aggregate processed notes into draft report using LLM.

    Args:
        state: Current workflow state

    Returns:
        Updated state with draft report
    """
    logger.info("Aggregating draft report")

    # Combine all processed notes
    all_notes = "\n\n---\n\n".join(
        f"## Query: {query}\n\n{notes}"
        for query, notes in state.processed_notes.items()
    )

    prompt = f"""Based on the following research notes, create a comprehensive report
answering the original question.

Original Question: {state.user_prompt}

Research Notes:
{all_notes}

Create a well-structured markdown report in {state.language}."""

    try:
        # TODO: Implement actual LLM call
        # For now, create placeholder
        state.draft_report = f"# Draft Report\n\n{all_notes}"
        logger.info("Draft report created")

    except Exception as e:
        logger.error(f"Draft aggregation failed: {e}")
        state.error_log.append(f"Draft error: {str(e)}")

    return state
```

#### `agents/nodes/validation_controller.py`
```python
from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def validation_controller(state: HermesState) -> HermesState:
    """
    Control validation loop - decide whether to continue or finish.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation completion flag
    """
    logger.info(f"Validation controller: loop {state.loop_count}/{state.max_validation}")

    # Check if we've done minimum loops
    if state.loop_count < state.min_validation:
        logger.info("Continuing validation (below minimum)")
        state.validation_complete = False
        return state

    # Check if we've hit maximum loops
    if state.loop_count >= state.max_validation:
        logger.info("Validation complete (maximum reached)")
        state.validation_complete = True
        return state

    # TODO: Add quality check logic here
    # For now, just complete after min loops
    logger.info("Validation complete (minimum satisfied)")
    state.validation_complete = True

    return state
```

#### `agents/nodes/validator.py`
```python
from hermes_cli.agents.state import HermesState
from hermes_cli.tools import OllamaClient
import logging

logger = logging.getLogger(__name__)


def validator(state: HermesState) -> HermesState:
    """
    Validate and improve draft report.

    Args:
        state: Current workflow state

    Returns:
        Updated state with improved draft
    """
    logger.info(f"Validating report (loop {state.loop_count})")

    if not state.draft_report:
        logger.warning("No draft to validate")
        return state

    prompt = f"""Review and improve the following report draft:

{state.draft_report}

Check for:
- Factual accuracy
- Completeness
- Clarity
- Structure

Provide an improved version."""

    try:
        # TODO: Implement actual LLM call
        # For now, keep draft as-is
        logger.info("Validation complete (placeholder)")
        state.loop_count += 1

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        state.error_log.append(f"Validation error: {str(e)}")

    return state
```

#### `agents/nodes/final_reporter.py`
```python
from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def final_reporter(state: HermesState) -> HermesState:
    """
    Finalize report with metadata and formatting.

    Args:
        state: Current workflow state

    Returns:
        Updated state with final validated report
    """
    logger.info("Creating final report")

    if not state.draft_report:
        logger.error("No draft report available")
        state.validated_report = "# Error\n\nNo report could be generated."
        return state

    # Add metadata header
    metadata = f"""---
query: {state.user_prompt}
language: {state.language}
queries_generated: {len(state.queries)}
sources_collected: {sum(len(r) for r in state.query_results.values())}
validation_loops: {state.loop_count}
---

"""

    state.validated_report = metadata + state.draft_report
    logger.info("Final report complete")

    return state
```

### 3. Implement `agents/graph.py`

Create the main LangGraph workflow:

```python
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
    """
    Routing function for validation loop.

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
    """
    Create and configure the Hermes workflow graph.

    Returns:
        Configured LangGraph workflow
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
```

### 4. Update `agents/__init__.py`

```python
"""
Agents package for Hermes.

Contains LangGraph workflow definition and node implementations
for the research and reporting pipeline.
"""

from .graph import create_hermes_workflow
from .state import HermesState

__all__ = [
    "create_hermes_workflow",
    "HermesState",
]
```

## Implementation Notes

### LangGraph Integration
- Use LangGraph's `Graph` class for workflow orchestration
- Nodes are Python functions that take and return state
- Use conditional edges for validation loop control
- State is automatically passed between nodes

### Error Handling
- Each node should handle its own errors gracefully
- Log errors to state.error_log
- Don't let one query failure stop entire workflow
- Continue with partial results when possible

### TODO Markers
- Leave TODO comments where actual LLM/browser/container integration needed
- These will be connected to actual tools in later phases
- For now, use placeholders to test workflow structure

### Logging
- Log entry/exit of each node
- Log progress within nodes (e.g., "Processing query 2/5")
- Include relevant context in log messages

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/agents/`:
1. `state.py` - Pydantic state model
2. `graph.py` - LangGraph workflow definition
3. `nodes/__init__.py` - Node exports
4. `nodes/prompt_normalizer.py`
5. `nodes/query_generator.py`
6. `nodes/web_researcher.py`
7. `nodes/container_processor.py`
8. `nodes/draft_aggregator.py`
9. `nodes/validation_controller.py`
10. `nodes/validator.py`
11. `nodes/final_reporter.py`
12. `__init__.py` - Package exports

## Resources

- Design document sections: 6.4, 9
- LangGraph documentation: https://langchain-ai.github.io/langgraph/
- Tools layer (from Phase 1 Task 3)

## Success Criteria

- Complete workflow graph defined
- All 8 nodes implemented with proper signatures
- State model properly defined with Pydantic
- Validation loop routing works correctly
- Can be imported: `from hermes_cli.agents import create_hermes_workflow, HermesState`
- Workflow can be instantiated without errors
- Placeholder implementations allow testing of workflow structure
