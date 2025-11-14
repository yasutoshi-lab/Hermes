# Task: Wire LangGraph Nodes to Ollama

**Task ID**: task_llm_wiring
**Priority**: high
**Assigned to**: worker-2
**Dependencies**: Coordinates with task_browser_fallback for richer inputs but can proceed independently

## Objective
Move the workflow beyond placeholders by making `query_generator`, `draft_aggregator`, and `validator` call the real `OllamaClient` with user-configured parameters, so `hermes run --prompt ...` produces LLM-generated queries and reports when an Ollama server is available.

## Context
- `hermes_cli/services/run_service.py` already loads config overrides but never passes the Ollama settings to the LangGraph nodes.
- The nodes in `hermes_cli/agents/nodes/` still contain TODO comments and dummy strings (e.g., `Query 1 for ...`).
- Without LLM output the downstream pipeline can never produce meaningful drafts/validation, blocking parity with the detailed design doc §9–10.

## Requirements
- Extend `HermesState` to carry the minimal Ollama call context (`api_base`, `model`, `retry`, `timeout_sec`) plus a lightweight helper for building chat messages.
- Update `RunService.run_prompt()` to instantiate a reusable `OllamaConfig` from the resolved config and pass it into the workflow state (or inject a callable) so every node can build an `OllamaClient` on demand without re-reading files.
- Refactor the following nodes to call Ollama:
  1. `query_generator`: feed a structured prompt (include language, desired query count) and parse the numbered/line-separated response into `state.queries`; add defensive parsing so malformed LLM output doesn’t crash the run.
  2. `draft_aggregator`: send the combined research notes to Ollama and store the response verbatim as `state.draft_report`.
  3. `validator`: prompt Ollama to critique/improve the draft, increment the loop counter, and overwrite `state.draft_report` with the improved version.
- Share code where it makes sense (e.g., helper in `hermes_cli/tools/ollama_client.py` for `build_client(config)` or injecting a client factory into the state) to avoid re-copying retry logic.
- Provide mock-friendly seams so unit tests can run without a live Ollama daemon: for example, allow `RunService` to accept an optional `ollama_client_factory` argument that defaults to the real client but can be overridden in tests.
- Add unit tests under `tests/` that stub the factory and assert:
  - `query_generator` stores parsed queries when the stub returns canned responses.
  - `draft_aggregator` and `validator` call the stub with the expected prompts and update the state accordingly.
  - `RunService.run_prompt()` passes overrides (e.g., `--model`, `--min-validation`) down into the client factory/state.
- Update docs to mention the need to run `ollama serve` (README + DEVELOPMENT) and that the CLI now performs actual LLM calls.

## Expected Output
- Updated state, service, and node modules with real Ollama calls plus supporting tests/documentation.
- Worker report should mention which tests were executed (e.g., new unit tests, existing smoke scripts).

## Resources
- State + workflow: `hermes_cli/agents/state.py`, `hermes_cli/agents/nodes/*.py`, `hermes_cli/agents/graph.py`
- Service: `hermes_cli/services/run_service.py`
- Ollama client: `hermes_cli/tools/ollama_client.py`
- Tests/docs: `tests/`, `README.md`, `DEVELOPMENT.md`
