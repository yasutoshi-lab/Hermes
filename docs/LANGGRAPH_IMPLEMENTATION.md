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

#### 2. SearchNode
**Purpose**: Gather information using web-search-mcp

**Inputs**:
- query (string to search for)

**Outputs**:
- search_results (list of search hits with full content)

**Processing**:
1. Call web-search-mcp `full-web-search` tool
2. Parse results (title, URL, description, content)
3. Handle search failures with retry/fallback
4. Store results in state

**Design Reference**: Uses web-search-mcp's multi-engine search (Google → DuckDuckGo fallback)

#### 3. ProcessingNode
**Purpose**: Process data in isolated container environment

**Inputs**:
- search_results (raw web content)

**Outputs**:
- processed_data (parsed and extracted information)

**Processing**:
1. Create isolated container via container-use
2. Parse HTML/PDF documents
3. Extract structured information
4. Store processed data with metadata
5. Clean up container resources

**Design Reference**: Uses container-use for safe, isolated execution

#### 4. LLMNode
**Purpose**: Generate provisional answer using local LLM

**Inputs**:
- query (user's question)
- processed_data (analyzed information)
- model_name (LLM to use)

**Outputs**:
- provisional_answer (candidate response)

**Processing**:
1. Construct prompt with query and context
2. Call Ollama with specified model (default: gpt-oss:20b)
3. Parse LLM response
4. Store provisional answer for verification

**Design Reference**: Uses Ollama's local LLM execution with configurable models

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

#### 6. ReportNode
**Purpose**: Generate final Markdown report

**Inputs**:
- provisional_answer (verified content)
- language (output language)
- search_results (sources)
- verification_count (processing depth)

**Outputs**:
- final_report (formatted Markdown)

**Processing**:
1. Format provisional_answer as Markdown
2. Add metadata (sources, timestamp, model)
3. Localize based on language preference
4. Save to history_path
5. Optionally convert to PDF

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
from src.orchestrator import run_workflow

# Simple query execution
result = run_workflow(
    query="LangGraphについて教えて",
    language="ja",
    model_name="gpt-oss:20b"
)

print(result["final_report"])
```

### Example 2: Manual State Initialization
```python
from src.state import create_initial_state
from src.orchestrator import compile_workflow

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
from src.orchestrator import create_workflow

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
from src.orchestrator import visualize_workflow

# Generate workflow visualization
visualize_workflow("docs/workflow_diagram.png")
```

### Example 5: Streaming Execution
```python
from src.state import create_initial_state
from src.orchestrator import compile_workflow

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
from src.orchestrator import input_node
from src.state import create_initial_state

# Test individual node
state = create_initial_state(query="test query")
result = input_node(state)

assert "messages" in result
print("Node test passed")
```

### Integration Testing Workflow
```python
from src.orchestrator import compile_workflow
from src.state import create_initial_state

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
