# Verification Flow & LLM Handoff

This document expands on 基本設計書 Section 5 and explains how the new LLM/Report implementations coordinate with the verification loop.

## 1. Provisional Answer Contract

After `processing_node` normalizes evidence, `llm_node` produces a provisional answer plus metadata:

- `provisional_answer` always includes:
  - Intro paragraph with `[S#]` citations
  - `Key Findings` bullet list (3–5 items, each with citations)
  - `Verification Targets` bullet list (<=2 follow-up actions)
- `llm_metadata` captures:
  - `citations`: ordered list of `{id, title, url}` entries matching `[S#]`
  - `context_items`: how many processed snippets were fed to the LLM
  - `history_log`: path to `sessions/<id>/llm_summary.md`
- Errors encountered during retries are appended to `state["errors"]` even if a later attempt succeeds, so the orchestrator can surface partial degradations.

## 2. Verification Inputs

`verification_node` relies on several signals produced upstream:

| Source | Field | Purpose |
|--------|-------|---------|
| `llm_node` | `provisional_answer` | Raw text to extract claims from |
| `llm_node` | `llm_metadata.citations` | Mapping of `[S#]` to canonical URLs |
| `processing_node` | `processed_data` | Rich corpus used for claim scoring |
| `search_node` | `search_results` | Supplemental snippets when claims lack coverage |
| History | `llm_summary.md` | Debug trace containing the evidence summary handed to the LLM |

The verification logic pulls structured claims via `nodes.utils.claims.extract_claims`, then:

1. Builds a corpus from `search_results` and any verification-triggered follow-up searches.
2. Scores each claim, classifies it (`pass/review/fail`), and decides whether another loop is required.
3. Persists outcomes into `verified.md` within the session directory so later CLI invocations can surface the audit trail.

## 3. Report Loop Closure

The verification summary feeds the report node through:

- `state["verification_summary"]` — contains totals, pass counts, average confidence, and `needs_additional_search`.
- `state["verification_count"]` — number of completed loops, embedded in both Markdown metadata and CLI messaging.

`report_node` adds a localized verification section that mirrors this state:

```markdown
## Verification Status
- Verification loops: 1
- Avg confidence: 0.76
- Claims validated: 3/3
- Additional research required: no
```

If verification requests another loop, `should_continue_verification` routes back to `search_node`, otherwise the report node executes and archives the final deliverables.

## 4. Files Written per Iteration

| Node | File | Description |
|------|------|-------------|
| LLM | `llm_summary.md` | Evidence snapshot + provisional excerpt (for inspectors/tests) |
| Verification | `verified.md` | Append-only log of claim scores and rerun decisions |
| Report | `report.md` / `report.pdf` | Final user-facing output |

All files live under `sessions/<session_id>/` and are created only when `history_path` exists to keep automated tests hermetic.
