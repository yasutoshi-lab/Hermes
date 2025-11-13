# Search Pipeline

This document captures the concrete search behavior implemented for the Hermes LangGraph workflow. It formalizes the interface between SearchNode, VerificationNode, and any other component that needs web evidence.

## 1. MCP Client Architecture

- The `WebSearchClient` (`src/modules/mcp_client.py`) wraps the `web-search-mcp` tools `full-web-search`, `get-web-search-summaries`, `get-single-web-page-content`, and provides a `multi_search` helper.
- Connection parameters:
  - Base URL: `settings.web_search_mcp_endpoint` (default `http://localhost:3000`)
  - Timeout: `settings.timeout_seconds`
  - Retries: `settings.max_retries` with exponential backoff (0.5s * 2^(attempt-1))
  - Optional API key through `Authorization: Bearer <key>`
- Responses are normalized to the `SearchResult` typed dict with keys:
  - `title`, `url`, `description`, `content`, `language`, `retrieved_at`, optional `score`

## 2. Query Strategy

1. **Primary search**: `full-web-search` with language-aware shaping.
   - Japanese queries append `最新情報` if not already present.
   - English queries append `latest insights`.
   - Result limit defaults to `settings.default_search_limit` (5).
2. **Fallback summary search**: `get-web-search-summaries` when the number of enriched results is below the limit.
3. **Follow-up heuristics**: Generate up to three supplemental queries per language:
   - Japanese: `根拠`, `事例`, `最新ニュース`
   - English: `supporting data`, `case study`, `regulatory context`
   - Execute through `multi_search`, deduplicate by URL.
4. **Targeted fetches**: Up to three URLs missing `content` are re-queried via `get-single-web-page-content` to capture full bodies for verification.

The node strives to return ≥5 enriched results; when the ecosystem cannot produce that many, it still returns whatever evidence is available and records the shortage in `state["errors"]`.

## 3. Retry & Rate Limit Handling

- HTTP 429 triggers a `RateLimitError` and automatic retry with backoff.
- Server errors (>=500) also trigger retries; malformed JSON raises `MCPClientError`.
- After exhausting retries, SearchNode logs the failure, appends an error message, and continues with any partial data.

## 4. Data Contract

SearchNode writes objects shaped as:

```json
{
  "title": "Result title",
  "url": "https://example.com",
  "summary": "Short description or content excerpt",
  "content": "<normalized body>",
  "language": "ja|en",
  "retrieved_at": "2024-01-01T00:00:00Z"
}
```

- HistoryManager receives the same data so investigators can review `search_results.md`.
- VerificationNode and ProcessingNode can assume `content` is filled for at least the top few entries; when not, `summary` contains a snippet to guide re-processing.

## 5. Coordination with Verification

- Verification (worker-1 scope) should reuse `WebSearchClient` for re-querying claims. The client is thread-safe for read-heavy usage because it relies on a shared requests session.
- Claims detected as risky can call `summary_search` when only lightweight confirmation is needed, or `fetch_page_content` for targeted URL validation.
- All errors bubble via `state["errors"]` to keep the orchestrator aware of degraded conditions, enabling additional retries or a manual intervention prompt.
