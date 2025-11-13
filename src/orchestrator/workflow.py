"""
LangGraph Workflow for Research Analyst Agent

This module defines the workflow graph structure that orchestrates the research
analyst agent. The workflow consists of multiple nodes that process user queries,
search for information, verify results, and generate final reports.

Design Reference:
    基本設計書.md Section 4.1 - Node Configuration
    基本設計書.md Section 5 - Processing Flow
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState, add_error, increment_verification_count


# ============================================================================
# Node Implementations (Stub Functions)
# ============================================================================

def input_node(state: AgentState) -> dict:
    """
    Input Node: Receives user prompt and configuration.

    This node processes the initial user input, validates the query, and sets up
    the initial state configuration. It extracts the query, language preference,
    and model selection from user input.

    Args:
        state: Current agent state

    Returns:
        dict: State updates with validated input

    Processing Steps:
        1. Extract query from messages or state
        2. Detect or validate language setting
        3. Validate model_name is available
        4. Set up history_path if not already set

    Design Reference:
        基本設計書.md Section 4.1 - InputNode
    """
    print("[InputNode] Processing user input...")

    # Stub implementation: validate that we have a query
    if not state.get("query"):
        return add_error(state, "No query provided")

    # In real implementation, would extract query from messages,
    # detect language, validate model availability, etc.

    return {
        "messages": [{"role": "system", "content": f"Processing query: {state['query']}"}]
    }


def search_node(state: AgentState) -> dict:
    """
    Search Node: Performs web search using web-search-mcp.

    This node calls the full-web-search or get-web-search-summaries tool from
    web-search-mcp to gather relevant information for the user's query. It handles
    search failures and can retry with adjusted parameters.

    Args:
        state: Current agent state with query

    Returns:
        dict: State updates with search_results

    Processing Steps:
        1. Extract query from state
        2. Call web-search-mcp full-web-search tool
        3. Parse and store results with title, URL, content
        4. Handle search failures with fallback strategies

    Design Reference:
        基本設計書.md Section 4.1 - SearchNode
        基本設計書.md Section 2.2 - Web Search MCP Server
    """
    print(f"[SearchNode] Searching for: {state.get('query', 'N/A')}")

    # Stub implementation: simulate search results
    stub_results = [
        {
            "title": "LangGraph Documentation",
            "url": "https://langchain-ai.github.io/langgraph/",
            "description": "Official LangGraph documentation",
            "content": "LangGraph is a library for building stateful, multi-actor applications..."
        }
    ]

    return {
        "search_results": stub_results,
        "messages": [{"role": "system", "content": f"Found {len(stub_results)} search results"}]
    }


def processing_node(state: AgentState) -> dict:
    """
    Processing Node: Processes data in isolated container environment.

    This node uses container-use to safely process search results in an isolated
    environment. It parses documents, extracts structured data, and performs any
    necessary transformations without affecting the host system.

    Args:
        state: Current agent state with search_results

    Returns:
        dict: State updates with processed_data

    Processing Steps:
        1. Retrieve search_results from state
        2. Create isolated container environment
        3. Parse and extract relevant information
        4. Store processed data with metadata
        5. Clean up container resources

    Design Reference:
        基本設計書.md Section 4.1 - ProcessingNode
        基本設計書.md Section 2.3 - Container Use
    """
    print("[ProcessingNode] Processing data in container...")

    search_results = state.get("search_results", [])

    # Stub implementation: simulate processed data
    stub_processed = [
        {
            "source": result.get("url", "unknown"),
            "extracted_info": f"Processed: {result.get('title', 'N/A')}",
            "timestamp": "2025-11-13T20:41:00Z"
        }
        for result in search_results
    ]

    return {
        "processed_data": stub_processed,
        "messages": [{"role": "system", "content": f"Processed {len(stub_processed)} documents"}]
    }


def llm_node(state: AgentState) -> dict:
    """
    LLM Node: Generates provisional answer using local LLM.

    This node calls the local LLM (default: gpt-oss:20b via Ollama) to analyze
    processed data and generate a provisional answer. The answer is based on
    search results and processed information.

    Args:
        state: Current agent state with processed_data

    Returns:
        dict: State updates with provisional_answer

    Processing Steps:
        1. Retrieve processed_data and query
        2. Construct prompt for LLM with context
        3. Call Ollama with specified model_name
        4. Parse LLM response and extract answer
        5. Store provisional answer for verification

    Design Reference:
        基本設計書.md Section 4.1 - LLMNode
        基本設計書.md Section 2.4 - LLM and Ollama
    """
    print(f"[LLMNode] Generating answer with model: {state.get('model_name', 'N/A')}")

    # Stub implementation: simulate LLM response
    query = state.get("query", "")
    processed_count = len(state.get("processed_data", []))

    stub_answer = f"""
Based on the analysis of {processed_count} sources regarding "{query}":

[Provisional Answer]
This is a stub implementation. In production, this would contain the actual
LLM-generated response based on processed data and search results.

Key findings:
- Information extracted from web search
- Analysis from container processing
- Synthesized answer to user query
"""

    return {
        "provisional_answer": stub_answer,
        "messages": [{"role": "assistant", "content": "Generated provisional answer"}]
    }


def verification_node(state: AgentState) -> dict:
    """
    Verification Node: Verifies provisional answer accuracy.

    This node examines the provisional answer for factual accuracy, consistency,
    and completeness. It may trigger additional search loops if verification fails
    or information is insufficient.

    Args:
        state: Current agent state with provisional_answer

    Returns:
        dict: State updates with verification results and incremented count

    Processing Steps:
        1. Extract key claims from provisional_answer
        2. Cross-reference with search_results
        3. Identify contradictions or missing information
        4. Increment verification_count
        5. Determine if another search loop is needed

    Design Reference:
        基本設計書.md Section 4.1 - VerificationNode
        基本設計書.md Section 5 - Verification Loop
    """
    print("[VerificationNode] Verifying answer accuracy...")

    current_count = state.get("verification_count", 0)
    update = increment_verification_count(state)

    # Stub implementation: simple verification logic
    # In production, would perform actual fact-checking
    verification_passed = current_count >= 1  # Pass after first verification

    update["messages"] = [
        {
            "role": "system",
            "content": f"Verification loop {current_count + 1}: {'Passed' if verification_passed else 'Needs refinement'}"
        }
    ]

    return update


def report_node(state: AgentState) -> dict:
    """
    Report Node: Generates final Markdown report.

    This node takes the verified provisional answer and formats it as a final
    Markdown report in the user's preferred language. The report is saved to
    the history path and returned to the user.

    Args:
        state: Current agent state with verified provisional_answer

    Returns:
        dict: State updates with final_report

    Processing Steps:
        1. Retrieve provisional_answer and language
        2. Format answer as Markdown report
        3. Add metadata (sources, timestamp, etc.)
        4. Save to history_path
        5. Optionally convert to PDF

    Design Reference:
        基本設計書.md Section 4.1 - ReportNode
        基本設計書.md Section 6 - History Management
    """
    print("[ReportNode] Generating final report...")

    provisional = state.get("provisional_answer", "")
    language = state.get("language", "ja")
    query = state.get("query", "")

    # Stub implementation: format as Markdown report
    report_title = "研究レポート" if language == "ja" else "Research Report"

    stub_report = f"""# {report_title}

## Query
{query}

## Summary
{provisional}

## Sources
{len(state.get('search_results', []))} sources analyzed

## Verification
Completed {state.get('verification_count', 0)} verification loops

---
Generated by Research Analyst Agent
Model: {state.get('model_name', 'N/A')}
"""

    return {
        "final_report": stub_report,
        "messages": [{"role": "assistant", "content": "Final report generated"}]
    }


# ============================================================================
# Conditional Edge Functions
# ============================================================================

def should_continue_verification(state: AgentState) -> Literal["search_node", "report_node"]:
    """
    Conditional edge: Determines if verification loop should continue.

    This function decides whether the workflow should return to search_node for
    additional information gathering or proceed to report_node for final output.

    Args:
        state: Current agent state with verification results

    Returns:
        str: Next node name - either "search_node" or "report_node"

    Decision Logic:
        - If verification_count < max_loops AND verification failed: -> search_node
        - Otherwise: -> report_node

    Design Reference:
        基本設計書.md Section 4.1 - Verification Loop
    """
    verification_count = state.get("verification_count", 0)
    max_verification_loops = 3  # Configurable limit

    # Stub logic: continue if under limit and verification suggests need
    # In production, would check actual verification results
    if verification_count < max_verification_loops:
        # Check if verification indicated need for more search
        # For stub: only do one verification loop
        if verification_count < 1:
            return "search_node"

    return "report_node"


# ============================================================================
# Workflow Creation
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow.

    This function builds the complete workflow graph by:
    1. Creating a StateGraph with AgentState
    2. Adding all node functions
    3. Defining edges between nodes
    4. Setting up conditional routing
    5. Compiling with checkpoint support

    Returns:
        StateGraph: Compiled workflow ready for execution

    Workflow Structure:
        START → input_node → search_node → processing_node → llm_node →
        verification_node → [conditional: search_node OR report_node] → END

    Design Reference:
        基本設計書.md Section 4 - LangGraph Workflow Design

    Example:
        >>> workflow = create_workflow()
        >>> result = workflow.invoke({"query": "LangGraphについて", "language": "ja"})
        >>> print(result["final_report"])
    """
    # Initialize the StateGraph with our AgentState type
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("input_node", input_node)
    workflow.add_node("search_node", search_node)
    workflow.add_node("processing_node", processing_node)
    workflow.add_node("llm_node", llm_node)
    workflow.add_node("verification_node", verification_node)
    workflow.add_node("report_node", report_node)

    # Define the graph edges
    # Linear flow: input → search → processing → llm → verification
    workflow.add_edge("input_node", "search_node")
    workflow.add_edge("search_node", "processing_node")
    workflow.add_edge("processing_node", "llm_node")
    workflow.add_edge("llm_node", "verification_node")

    # Conditional edge: verification can loop back or proceed to report
    workflow.add_conditional_edges(
        "verification_node",
        should_continue_verification,
        {
            "search_node": "search_node",
            "report_node": "report_node"
        }
    )

    # Report node leads to END
    workflow.add_edge("report_node", END)

    # Set the entry point
    workflow.set_entry_point("input_node")

    return workflow


def compile_workflow() -> StateGraph:
    """
    Compiles the workflow with checkpointing enabled.

    This function creates the workflow and compiles it with MemorySaver for
    checkpoint support, enabling durable execution and recovery.

    Returns:
        StateGraph: Compiled workflow with checkpointing

    Example:
        >>> app = compile_workflow()
        >>> config = {"configurable": {"thread_id": "session_001"}}
        >>> result = app.invoke(initial_state, config)
    """
    workflow = create_workflow()

    # Compile with memory checkpointing for durable execution
    checkpointer = MemorySaver()
    compiled = workflow.compile(checkpointer=checkpointer)

    return compiled


def visualize_workflow(output_path: str = "workflow_graph.png") -> None:
    """
    Visualizes the workflow graph structure.

    Creates a visual representation of the workflow graph showing all nodes
    and edges. Requires graphviz to be installed.

    Args:
        output_path: Path where the visualization should be saved

    Example:
        >>> visualize_workflow("docs/workflow.png")

    Note:
        This function requires the graphviz package and system dependencies.
        Install with: pip install graphviz && apt-get install graphviz (Linux)
    """
    try:
        workflow = create_workflow()
        # LangGraph provides get_graph() for visualization
        graph = workflow.get_graph()

        # Draw the graph (requires graphviz)
        png_data = graph.draw_mermaid_png()

        with open(output_path, "wb") as f:
            f.write(png_data)

        print(f"Workflow visualization saved to: {output_path}")

    except ImportError:
        print("Warning: graphviz not installed. Skipping visualization.")
        print("Install with: pip install graphviz")
    except Exception as e:
        print(f"Error creating visualization: {e}")


# ============================================================================
# Workflow Execution Helpers
# ============================================================================

def run_workflow(query: str, language: str = "ja", model_name: str = "gpt-oss:20b") -> dict:
    """
    Convenience function to run the workflow with a query.

    Args:
        query: User's research query
        language: Preferred language ('ja' or 'en')
        model_name: LLM model to use

    Returns:
        dict: Final state with completed report

    Example:
        >>> result = run_workflow("LangGraphの使い方", language="ja")
        >>> print(result["final_report"])
    """
    from src.state import create_initial_state

    # Create initial state
    initial_state = create_initial_state(
        query=query,
        language=language,
        model_name=model_name
    )

    # Compile and run workflow
    app = compile_workflow()
    config = {"configurable": {"thread_id": f"session_{query[:20]}"}}

    result = app.invoke(initial_state, config)

    return result
