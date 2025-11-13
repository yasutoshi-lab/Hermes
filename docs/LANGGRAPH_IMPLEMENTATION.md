# LangGraph Implementation Documentation

## Overview

This document explains the LangGraph state definitions and workflow structure for the Research Analyst Agent. The implementation follows the design specified in `基本設計書.md` and uses LangGraph's StateGraph API for orchestration.

## State Structure

### AgentState TypedDict

The `AgentState` is the central data structure shared across all workflow nodes. It follows LangGraph best practices by storing only long-term necessary data, with transformations performed in each node.

```python
class AgentState(TypedDict):
    messages: Annotated[list[dict], add_messages]
    query: str
    search_results: list[dict]
    processed_data: list[dict]
    provisional_answer: str
    final_report: str
    language: str
    model_name: str
    history_path: str
    verification_count: int
    errors: list[str]
```

### State Field Descriptions

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `messages` | `list[dict]` | User and agent dialogue history | Uses `add_messages` reducer to append without duplication |
| `query` | `str` | Current search query | Extracted from user input by input_node |
| `search_results` | `list[dict]` | Web search results | Contains title, URL, description, full content from web-search-mcp |
| `processed_data` | `list[dict]` | Container-processed data | Parsed documents, extracted info from container-use |
| `provisional_answer` | `str` | Pre-verification answer | LLM-generated response before fact-checking |
| `final_report` | `str` | Verified Markdown report | Final output delivered to user |
| `language` | `str` | User's language preference | Either 'ja' (Japanese) or 'en' (English) |
| `model_name` | `str` | LLM model identifier | Default: 'gpt-oss:20b', configurable |
| `history_path` | `str` | Session history save path | Format: 'session_<timestamp>' |
| `verification_count` | `int` | Verification loops executed | Prevents infinite loops, tracks depth |
| `verification_summary` | `dict` | Latest verification aggregate metrics | Stores pass counts, confidence, and routing flag |
| `errors` | `list[str]` | Error messages | Debugging and user feedback |

## Workflow Architecture

### Node Descriptions

#### 1. InputNode
**Purpose**: Process initial user input and configuration

**Inputs**:
- Raw user messages
- Query string
- Language preference
- Model selection

**Outputs**:
- Validated query
- Configured language
- Validated model_name
- Initialized history_path

**Processing**:
1. Extract query from messages
2. Detect or validate language
3. Verify model availability
4. Set up session history path

See [docs/input_node.md](input_node.md) for heuristics, error handling, and the reusable `prepare_initial_context` helper that powers the CLI/REPL flows.

#### 2. SearchNode
**Purpose**: Gather information using web-search-mcp with resilient multi-strategy queries.

**Inputs**:
- `query` (string to search for)
- `language` (ja/en)
- `history_path` (for audit trail persistence)

**Outputs**:
- `search_results` (list of dicts containing `title`, `url`, `summary`, `content`, `language`, `retrieved_at`)
- `errors` (appended only when we encounter partial failures)

**Processing**:
1. Instantiate `WebSearchClient` (`src/modules/mcp_client.py`) which wraps `full-web-search`, `get-web-search-summaries`, and `get-single-web-page-content` with retry/backoff.
2. Execute `full-web-search` using language-aware query shaping (adds `最新情報` for Japanese queries, `latest insights` for English) and normalize the payload.
3. If the number of enriched results is < `settings.default_search_limit` (default 5), fall back to `get-web-search-summaries`.
4. Generate heuristic follow-up queries (根拠/事例/最新ニュース for Japanese, supporting data/case study/regulatory context for English) and run `multi_search` to broaden coverage.
5. Fetch full page bodies for up to three high-priority URLs that returned only snippets so downstream nodes always receive `content`.
6. Deduplicate by URL, attach ISO timestamps, and persist the raw payload to `HistoryManager.save_search_results`.

**Design Reference**: 基本設計書 Section 2.2/5 (search flow); web-search-mcp multi-engine behavior (Google→DuckDuckGo) plus retries on rate limits.

#### 3. ProcessingNode
**Purpose**: Process data in isolated container environment and emit structured snippets plus provenance.

**Inputs**:
- `search_results` (normalized by SearchNode)
- `language`, `history_path`

**Outputs**:
- `processed_data` (list of dicts containing `source`, `normalized_content`, `snippets`, `key_facts`, `tables`, `provenance`, `timestamp`)
- `errors` (only if certain documents fail but others succeed)

**Processing**:
1. Instantiate `ContainerProcessor`, which can call container-use MCP (future) or run a local fallback pipeline. Remote mode is ready via `enable_remote=True`.
2. Deduplicate URLs and build document descriptors (`title`, `url`, `content`, `summary`, `retrieved_at`).
3. Detect content type (PDF vs HTML vs plain text) and convert to Markdown/text (`markdownify`/`pdfminer` when available, otherwise a lightweight HTML stripper).
4. Generate snippets (top 5 paragraphs), extract key facts (sentences containing numerics, delimiters, or bullet markers), and collect table-like blocks (`|` or tab-separated rows).
5. Attach provenance metadata (language, retrieval timestamp, processor type) and persist human-readable logs via `HistoryManager.save_processed_data`.
6. Surface non-fatal processor errors in `state["errors"]` while allowing downstream nodes to keep working with successful artifacts.

**Design Reference**: 基本設計書 Section 2.3/5 (container isolation) ensures heavy parsing is sandboxed; Section 4.1 describes how processed outputs feed LLM + verification nodes.

#### 4. LLMNode
**Purpose**: Transform processed evidence into a citation-rich provisional answer.

**Inputs**:
- `query` + `language` (determine localization and fallback)
- `processed_data` (primary evidence) with `search_results` as backup
- `model_name` and optional `llm_stream_callback`
- `history_path` (writing `llm_summary.md`)

**Outputs**:
- `provisional_answer` (LLM draft)
- `llm_metadata` (model, context size, citations, prompt length, history log path)
- Optional `errors` appended when retries/fallbacks occur

**Processing**:
1. `build_llm_prompt` condenses up to six processed entries into bullet summaries with `[S#]` citations and localized instructions (JA/EN).
2. Resolve `ModelManager` (preferring any injected mock) and attempt generation with exponential backoff by shrinking context windows before falling back to English prompts.
3. Support token streaming via `state["llm_stream_callback"]` while still returning the full response string.
4. Persist a lightweight audit trail (`sessions/<id>/llm_summary.md`) containing the context snapshot, citations, and provisional excerpt for verification/CLI views.
5. Return structured metadata so downstream nodes (verification/report/CLI) can trace which sources informed the draft.

**Design Reference**: 基本設計書 Section 4.1 (LLM node) & Section 6 (history). Prompt rules align with Section 4.3 (language requirements).

#### 5. VerificationNode
**Purpose**: Verify provisional answer accuracy

**Inputs**:
- provisional_answer (response to verify)
- search_results (original sources)

**Outputs**:
- Incremented verification_count
- Verification status (implicit in decision)

**Processing**:
1. Extract key claims from provisional_answer
2. Cross-reference with search_results
3. Identify contradictions or gaps
4. Increment verification_count
5. Determine if re-search is needed

**Design Reference**: Implements verification loop from 基本設計書.md Section 5

Additional implementation details (claim extraction heuristics, `SearchClient` contract, routing thresholds, and history output) live in [docs/verification_flow.md](verification_flow.md).

#### 6. ReportNode
**Purpose**: Produce localized Markdown/PDF deliverables that summarize the investigation and verification outcomes.

**Inputs**:
- `provisional_answer` (post-verification content)
- `language`, `model_name`, `verification_count`, `verification_summary`
- `search_results` + `processed_data` (for deduped citations)
- `history_path` (HistoryManager session directory) and optional `report_format`

**Outputs**:
- `final_report` (Markdown)
- `report_path` (filesystem path or empty string)
- `report_metadata` (sources, timestamps, verification stats, PDF info)
- Optional `errors` when persistence fails

**Processing**:
1. `format_sources()` merges processed evidence with residual search hits, assigns stable `[S#]` IDs, and emits Markdown-ready bullets.
2. Localized templates add Summary / Methodology / Sources / Verification / Metadata sections, embedding verification loop stats (pass counts, confidence averages, re-search recommendation).
3. Persist Markdown through `HistoryManager.save_report` and create `report.pdf` (real PDF via reportlab when available, otherwise a clearly labeled placeholder).
4. Surface paths + flags in `report_metadata` so the CLI can advertise Markdown/PDF artifacts immediately after generation.

**Design Reference**: 基本設計書 Section 4.1 (Report node), Section 5 (verification outputs), Section 6 (history persistence).

### Orchestrator & Dependency Injection
- `src/orchestrator/workflow.py` imports the production nodes and exposes a `WorkflowDependencies` dataclass. Tests/CLI can override specific nodes or inject shared clients (`WebSearchClient`, `ContainerProcessor`, `HistoryManager`, `ModelManager`) without monkey-patching globals.
- Every node is wrapped with structured logging plus optional `on_event` callbacks that receive `WorkflowEvent` payloads (node name, delta, timestamp). The CLI uses this to render live progress when `--verbose` is supplied.
- `should_continue_verification` now inspects `verification_summary` (`status`, `pass_ratio`, `average_confidence`, `needs_additional_search`) and enforces `settings.verification_max_loops`, `verification_pass_ratio`, and `verification_min_confidence` before looping back to `search_node`.
- `run_workflow` accepts either a `query` or full `messages` list along with overrides for language/model/history. When `stream=True` it returns a `WorkflowRunResult` containing the final state plus the ordered `WorkflowEvent` list; otherwise it returns the final `AgentState` dict for backwards compatibility.

## Workflow Execution Flow

### Linear Flow
```
START → input_node → search_node → processing_node → llm_node → verification_node
```

### Conditional Routing
```
verification_node → [Decision Point]
    ├─ If verification fails OR count < max_loops → search_node (loop back)
    └─ If verification passes OR count >= max_loops → report_node → END
```

### Flow Diagram
```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ input_node  │  Validate query, configure settings
└──────┬──────┘
       │
       ▼
┌─────────────┐ ◄──────────────────────┐
│ search_node │  Web search via MCP    │
└──────┬──────┘                        │
       │                               │
       ▼                               │
┌─────────────┐                        │
│processing_  │  Parse in container    │
│   node      │                        │
└──────┬──────┘                        │
       │                               │
       ▼                               │
┌─────────────┐                        │
│  llm_node   │  Generate answer       │
└──────┬──────┘                        │
       │                               │
       ▼                               │
┌─────────────┐                        │
│verification_│  Check accuracy        │
│    node     │                        │
└──────┬──────┘                        │
       │                               │
       ├─── Needs refinement ──────────┘
       │
       └─── Verified
       │
       ▼
┌─────────────┐
│ report_node │  Format final report
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     END     │
└─────────────┘
```

## State Interaction Patterns

### Reading State
Nodes read state fields directly:
```python
def my_node(state: AgentState) -> dict:
    query = state.get("query", "")
    results = state.get("search_results", [])
    # ... process ...
```

### Updating State
Nodes return a dictionary with updates:
```python
def my_node(state: AgentState) -> dict:
    # Compute new values
    new_data = process(state)

    # Return updates
    return {
        "processed_data": new_data,
        "messages": [{"role": "system", "content": "Processing complete"}]
    }
```

### State Reducers
List fields like `messages` use reducers to append:
```python
messages: Annotated[list[dict], add_messages]
# Each update appends to messages rather than replacing
```

### Error Handling
Use helper functions for consistent error handling:
```python
from src.state import add_error

def my_node(state: AgentState) -> dict:
    try:
        result = risky_operation()
        return {"data": result}
    except Exception as e:
        return add_error(state, f"Operation failed: {e}")
```

## Usage Examples

### Example 1: Basic Usage
```python
from orchestrator.workflow import run_workflow, WorkflowRunResult

# Simple query execution with streaming
result = run_workflow(
    query="LangGraphについて教えて",
    language="ja",
    model_name="gpt-oss:20b",
    stream=True,
)

if isinstance(result, WorkflowRunResult):
    print(result.final_state["final_report"])
else:
    print(result["final_report"])
```

### Example 2: Manual State Initialization
```python
from state.agent_state import create_initial_state
from orchestrator.workflow import compile_workflow

# Create initial state
initial_state = create_initial_state(
    query="Explain LangGraph verification loops",
    language="en",
    model_name="gpt-oss:20b"
)

# Compile workflow
app = compile_workflow()

# Run with session ID for checkpointing
config = {"configurable": {"thread_id": "session_001"}}
result = app.invoke(initial_state, config)

print(f"Verification loops: {result['verification_count']}")
print(f"Final report:\n{result['final_report']}")
```

### Example 3: Accessing Workflow Graph
```python
from orchestrator.workflow import create_workflow

# Create workflow
workflow = create_workflow()

# Access graph structure
graph = workflow.get_graph()

# Print nodes
print("Nodes:", graph.nodes)

# Print edges
print("Edges:", graph.edges)
```

### Example 4: Visualization
```python
from orchestrator.workflow import visualize_workflow

# Generate workflow visualization
visualize_workflow("docs/workflow_diagram.png")
```

### Example 5: Streaming Execution
```python
from state.agent_state import create_initial_state
from orchestrator.workflow import compile_workflow

initial_state = create_initial_state(query="Research topic")
app = compile_workflow()
config = {"configurable": {"thread_id": "stream_session"}}

# Stream execution steps
for step in app.stream(initial_state, config):
    print(f"Step: {step}")
```

## Durable Execution

The workflow supports checkpointing for fault tolerance:

```python
from langgraph.checkpoint.memory import MemorySaver

# Compile with checkpointer
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Run with thread_id for state persistence
config = {"configurable": {"thread_id": "my_session"}}
result = app.invoke(initial_state, config)

# Resume from checkpoint if interrupted
result = app.invoke(None, config)  # Continues from last checkpoint
```

## Testing

### Unit Testing Nodes
```python
from nodes.input_node import input_node
from state.agent_state import create_initial_state

# Test individual node
state = create_initial_state(query="test query")
result = input_node(state)

assert "messages" in result
print("Node test passed")
```

### Integration Testing Workflow
```python
from orchestrator.workflow import compile_workflow
from state.agent_state import create_initial_state

# Test complete workflow
app = compile_workflow()
state = create_initial_state(query="test query")
result = app.invoke(state, {"configurable": {"thread_id": "test"}})

assert result["final_report"] != ""
assert result["verification_count"] > 0
print("Workflow test passed")
```

## Extension Points

### Adding New Nodes
```python
def custom_node(state: AgentState) -> dict:
    # Custom processing
    return {"custom_field": "value"}

# Add to workflow
workflow.add_node("custom_node", custom_node)
workflow.add_edge("existing_node", "custom_node")
```

### Custom Conditional Edges
```python
def custom_condition(state: AgentState) -> Literal["node_a", "node_b"]:
    if state.get("some_condition"):
        return "node_a"
    return "node_b"

workflow.add_conditional_edges(
    "decision_node",
    custom_condition,
    {"node_a": "node_a", "node_b": "node_b"}
)
```

## Design Principles

1. **State as Source of Truth**: All nodes read from and write to shared state
2. **Immutable Updates**: Nodes return new values, don't mutate state directly
3. **Minimal State**: Store only essential data, transform in nodes
4. **Error Resilience**: Use checkpointing and error tracking
5. **Modularity**: Each node has a single, well-defined responsibility
6. **Type Safety**: Use TypedDict and type hints throughout

## References

- Design Document: `基本設計書.md`
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- State Implementation: `src/state/agent_state.py`
- Workflow Implementation: `src/orchestrator/workflow.py`
