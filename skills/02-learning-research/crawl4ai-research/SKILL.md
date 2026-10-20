---
name: crawl4ai-research
description: Use Crawl4AI for LLM-ready web crawling, page extraction, research collection, Markdown conversion, structured extraction, screenshots, and dynamic-page scraping. Use when the user asks Codex to crawl websites, extract article/product/documentation content, collect citations from multiple URLs, convert web pages to clean Markdown, or build a reproducible web research workflow.
---

# Crawl4AI Research

Use Crawl4AI as a crawling and extraction backend when normal web browsing is too shallow, when results need to be saved as artifacts, or when a task needs repeatable extraction from one or many URLs.

## Workflow

1. Clarify the extraction target: pages, domains, depth, fields, output format, and whether screenshots or dynamic rendering are needed.
2. Check the local project environment before installing anything:
   - Look for an existing Python environment, lockfile, Docker setup, or project convention.
   - Run `crawl4ai --help`, `python -m crawl4ai --help`, or inspect installed packages if appropriate.
3. If Crawl4AI is not installed and the user wants executable crawling, ask for or request approval before network installation. Prefer the active project environment:
   - `pip install -U crawl4ai`
   - `crawl4ai-setup`
   - `crawl4ai-doctor`
4. Use the smallest interface that fits:
   - Use direct Codex web browsing for a few simple pages when citations are enough.
   - Use Crawl4AI CLI for quick one-off extraction when available.
   - Use Python `AsyncWebCrawler` for scripted, repeatable, batched, structured, or dynamic-page workflows.
   - Use Docker/MCP only when the user explicitly wants a service integration or repeatable external server.
5. Save outputs in the workspace when the user needs artifacts: Markdown, JSON, CSV, screenshots, or extraction logs.
6. Report source URLs, extraction assumptions, failed URLs, and any pages that required JavaScript or special handling.

## Python Pattern

Prefer the current documented API shape and verify it locally when installed. A typical extraction starts like this:

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        print(result.markdown)

asyncio.run(main())
```

For multiple URLs, keep concurrency conservative unless the user asks for speed. Respect robots, rate limits, login boundaries, and paywalls.

## Output Guidance

For research summaries, keep raw extracted content separate from the synthesized answer. Include:

- `sources`: original URL, title when available, fetch status, extraction timestamp
- `content`: cleaned Markdown or structured fields
- `notes`: dynamic rendering, blocked pages, truncation, retries, or selectors used

For structured extraction, define the target schema first and validate missing fields explicitly instead of silently guessing.

## Upstream

Crawl4AI is an external Python project, not a Codex skill. Treat this skill as a local operating guide for using it. Check upstream docs when exact CLI flags, setup commands, Docker options, or API arguments matter: https://github.com/unclecode/crawl4ai
