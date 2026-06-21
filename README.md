# Hacker News Tech Digest Agent

An automated agent that scans Hacker News, filters for tech stories, summarises each one with an LLM, and produces a concise, actionable daily digest for a product and engineering team.

## What it does

1. **Fetches** the current top stories from the Hacker News API.
2. **Summarises** each story with an LLM into a 2-3 sentence summary, a "why it matters" insight, and a topic tag.
3. **Filters** for tech relevance, grouping tech stories by topic and separating non-tech ones into an "Also trending" section.
4. **Generates** a readable Markdown digest, ready to be emailed or published.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows (source venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:

GEMINI_API_KEY=key

## Usage

```bash
python main.py                 # default: top 15 stories -> digest.md
python main.py --limit 10      # less stories
python main.py --out today.md  # custom output file
```

## Architecture

The pipeline is split into single-responsibility modules:

| Module | Responsibility                                                                                                                                                              |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `fetch.py` | Pulls top story IDs and details from the Hacker News API, with error handling so one failed story never breaks the run. |
| `summarise.py` | Calls the LLM and returns **structured, validated JSON** (summary, why-it-matters, topic). A malformed response degrades gracefully instead of crashing the digest. |
| `digest.py` | Orchestrates fetch + summarise (concurrently), filters for tech, and renders the Markdown report. |
| `main.py` | Clean CLI entry point with configurable limit and output. |

## Design decisions

- **Structured LLM output:** the model is prompted for strict JSON with a fixed topic enum, and every response is validated. This turns an unpredictable LLM into a reliable data source.
- **Concurrency:** summaries run in parallel (`ThreadPoolExecutor`), cutting runtime from minutes to seconds. Worker count is kept modest to respect the API's rate limits.
- **Graceful degradation:** network and parsing failures are caught per-story, so the agent always produces a digest.

## Next steps for production

- Schedule a daily unattended run (cron / GitHub Actions) so the digest is delivered every morning with zero manual effort. The email-send function is stubbed and ready to wire to a real provider (SMTP / SendGrid).
- De-duplicate stories across days so the digest only shows what's new.
- Rank by a blend of score and recency, and let the LLM surface cross-story trends.
- Add automated tests for the fetch and validation layers.