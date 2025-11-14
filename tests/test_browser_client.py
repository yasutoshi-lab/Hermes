"""Smoke test ensuring BrowserUseClient fallback returns data."""

from hermes_cli.tools import BrowserUseClient, BrowserUseError


def main() -> None:
    query = "Hermes autonomous research agent"
    with BrowserUseClient(max_sources=2) as client:
        results = client.search(query)

    if not results:
        raise SystemExit("DuckDuckGo fallback returned no results. Check network connectivity.")

    sample = results[0]
    print(f"Sample result: {sample.title} -> {sample.url}")
    print(f"Snippet: {sample.snippet[:160]}...")
    print(f"Content preview: {sample.content[:200]}...")
    print(f"Fetched {len(results)} total sources.")


if __name__ == "__main__":
    try:
        main()
    except BrowserUseError as exc:
        raise SystemExit(f"BrowserUseClient search failed: {exc}")
