# InputNode Guide

This document describes how Hermes initializes agent state inside `InputNode` and how other entry points (CLI, REPLs, tests) can reuse the same logic via `prepare_initial_context`.

## Responsibilities

InputNode follows 基本設計書.md Sections 4.1 / 5 step 1 and performs:

1. **Query extraction** – selects the most recent user message, normalizes whitespace, and stores the cleaned query in `state["query"]`.
2. **Language detection** – reuses `LanguageDetector` (Section 8 robustness requirements) to auto-detect JA/EN when users did not specify a language. Detection metadata (confidence + source) is surfaced to the user through localized system messages.
3. **Model + config resolution** – safely validates user-supplied `model_name`, otherwise falls back to `settings.default_model`.
4. **History warm-up** – allocates a new HistoryManager session when `history_path` is empty and persists the initial prompt to `input.md`. Failures are downgraded to warnings so the workflow can keep running without history.
5. **State messaging** – appends localized system messages to `state["messages"]` so the LangGraph reducer can see the latest language/model selection.

## LanguageDetector heuristics

`LanguageDetector` now ignores code fences, inline code, bare URLs, and Markdown links before counting characters. Mixed snippets such as:

```
Please explain the API.
```python
print("こんにちは")
```
https://example.com
```

correctly resolve to English because the natural-language portion dominates once noise is stripped. The helper also exposes `normalize_text` so other modules/tests can remove the same noise profile.

## `prepare_initial_context`

`prepare_initial_context` bundles the shared preprocessing logic so that non-LangGraph entry points can prepare state without duplicating validation code.

```python
from nodes.input_node import prepare_initial_context

messages = [{"role": "user", "content": "LangGraphとは何ですか？"}]
context = prepare_initial_context(messages)
state_updates = {
    "query": context["query"],
    "language": context["language"],
    "model_name": context["model_name"],
    "history_path": context["history_path"],
}
```

Key return fields:

- `language_confidence`: float in [0, 1] describing detector certainty.
- `system_messages`: ready-to-append LangGraph messages describing the session bootstrap.
- `warnings`: user-facing warnings (e.g., history temporarily disabled) that callers can surface however they like.

## Error handling & warnings

Fatal issues (missing messages, empty query) raise `InputPreparationError` and are reported through `state["errors"]`. History failures log warnings and add localized system messages like `Warning: History session could not be initialized (...)` so the UX remains transparent without breaking the workflow.

## Test coverage

`tests/test_nodes/test_input_node.py` exercises:

- JA/EN detection including mixed code blocks
- user-provided configs and history reuse
- empty input handling and invalid models
- warnings when HistoryManager initialization fails
- Unicode preservation and helper error paths

Complementary detector unit tests live in `tests/test_modules/test_language_detector.py` and verify detection, confidence scoring, and prompt templates.
