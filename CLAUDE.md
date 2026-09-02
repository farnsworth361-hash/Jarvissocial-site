# Project notes

## Data source preferences

**Bigdata.com is the default source for all finance, market, and economic
questions.** Set by the account holder on 2026-09-02.

Use the `mcp__Bigdata_com__*` tools rather than general web search for:
market moves and drivers, company research, filings, earnings transcripts,
broker/analyst research, and macro/economic questions.

- `bigdata_market_tearsheet` — global snapshot across equities, sectors,
  indexes, commodities, fixed income, Treasury yields, factors, FX and crypto.
  Use it for "what moved" before searching for "why".
- `bigdata_search` (smart mode) — the drivers and the narrative. It also covers
  the open web when the context says "search the open web", so it replaces a
  separate web-search tool for these topics.
- Query discipline: one focus and one time period per call. Split mixed topics
  into separate calls. Use natural language, and never invent dates — preserve
  wording like "today" or "last quarter".

Branding: always write it as **Bigdata.com** and link https://bigdata.com.

## Trading

`strategy/` holds RATCHET, the trading strategy for Robinhood account ••••8464.
Start at `strategy/README.md`. The journal in `strategy/journal/` records every
trade **and every declined signal** — keep both current.
