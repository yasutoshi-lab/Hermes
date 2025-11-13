# Processing Pipeline

This guide explains how ProcessingNode transforms raw `search_results` into structured `processed_data` artifacts that downstream nodes (LLM, Verification, Report) can consume safely.

## 1. Goals

- Normalize heterogeneous web content (HTML, PDF, plain text) into Markdown-like snippets.
- Deduplicate overlapping sources to keep the state lean.
- Extract key facts and table-like structures for fast referencing.
- Run heavy parsing inside an isolated container (container-use) when available, fall back to a deterministic local pipeline otherwise.

## 2. ContainerProcessor Abstraction

- Implemented in `src/nodes/processing_node.py` as `ContainerProcessor`.
- Parameters:
  - `base_url`: `settings.container_use_mcp_endpoint` (`http://localhost:3001` default)
  - `timeout`/`max_retries`: pulled from global settings
  - `enable_remote`: set to `True` once container-use RPC is wired; default `False` to keep unit tests offline.
- Remote mode payload:

```json
POST {base_url}/process
{
  "document": {...},
  "operations": ["normalize", "extract_facts", "extract_tables"]
}
```

- Failure in remote mode automatically falls back to local parsing so the workflow remains resilient.

## 3. Local Normalization Steps

1. **Content-type detection**:
   - Respect explicit `content_type` if provided
   - `.pdf` URLs ⇒ `application/pdf`
   - `<html` markers ⇒ `text/html`
   - Else default `text/plain`
2. **Conversion**:
   - HTML → Markdown via `markdownify` when available, otherwise a lightweight HTML stripper.
   - PDF → text via `pdfminer.high_level.extract_text` when installed; fallback to the raw string.
   - Plain text → whitespace-cleaned paragraphs.
3. **Snippets**:
   - Up to 5 paragraphs, shortened to 400 chars each and tagged with ordering metadata.
4. **Key facts**:
   - Sentences containing digits, colon separators, or bullet markers (・) are prioritized.
   - Falls back to the first sentence if nothing matches.
5. **Tables**:
   - Any block containing `|` or tab characters is treated as table-like data.

## 4. Deduplication & Provenance

- ProcessingNode tracks URLs to avoid re-processing duplicates from SearchNode.
- Each `processed_data` entry looks like:

```json
{
  "source": {
    "title": "...",
    "url": "https://example.com",
    "language": "ja|en",
    "content_type": "text/html",
    "retrieved_at": "2024-01-01T00:00:00Z"
  },
  "summary": "...",
  "normalized_content": "...",
  "snippets": [{"order": 1, "text": "..."}],
  "key_facts": ["fact1", "fact2"],
  "tables": ["table block"],
  "provenance": {"processor": "local|container-use", "notes": []},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

- HistoryManager receives condensed audit entries via `save_processed_data`, so investigators can track when and how each document was parsed.

## 5. Security & Isolation Assumptions

- All heavy parsing should eventually run inside container-use per 基本設計書 Section 2.3 to prevent untrusted HTML/JS from affecting the orchestrator.
- Local fallback is deterministic and avoids executing remote code; it only performs string-level transformations.
- When remote mode is enabled:
  - Always authenticate requests (API key header when provided).
  - Limit outbound network operations to container-use endpoints.
  - Record processor type (`provenance.processor`) so verification/reporting layers can audit which environment handled each artifact.

## 6. Integration Points

- **LLMNode** consumes `processed_data` (snippets + key facts) to ground responses.
- **VerificationNode** can re-check `key_facts` against the original `source.url`.
- **ReportNode** may embed excerpts from `normalized_content` while citing `source`.

Keeping the contract stable across these components ensures we can iterate on parsing quality (e.g., better HTML → Markdown) without rewriting downstream logic.
