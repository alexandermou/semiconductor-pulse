# Semiconductor Pulse

An English, mobile-friendly semiconductor market dashboard tracking **SOXL, NVDA, AMD, INTC, MU and QCOM**.

[Open the live dashboard](https://semiconductor-pulse-mou.alexandermou2000.chatgpt.site)

## Features

- Pre-market, regular-session and after-hours prices, percentage changes and available volume.
- Trading-day price sparklines and provider observation timestamps.
- Headline feed grouped by stock, covering earnings, guidance, industry announcements and market developments.
- Confirmed official sources, media reports and market speculation shown separately.
- Concise context about what happened, why it matters and potentially affected stocks.
- Stock, time-range, impact and evidence filters, plus headline search.
- One-minute refresh while open, with manual refresh and a countdown.
- Server-side historical snapshots and headline archive with 30-day retention; the archive UI shows up to 500 recent observations.
- A separately configured hourly background collection task supplements open-page refreshes.

## Stack

React 19, TypeScript, Vinext/Vite, Cloudflare Workers and Cloudflare D1. Data comes from public Yahoo Finance chart endpoints and Google News RSS, with Yahoo Finance search news as a fallback. Public feeds can be delayed, incomplete or rate-limited. Evidence, impact and summary context use conservative rules rather than independent fact verification. Source links and observation times are preserved.

## Development

Requires Node.js 22.13 or later.

```sh
npm ci
npm run db:generate  # only after a schema change
npm run build
node --import ./scripts/sites-env.mjs ./node_modules/wrangler/bin/wrangler.js d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file drizzle/0000_worthless_tyrannus.sql
npm run dev
```

Apply the existing migration once to a new local database. Do not replay an already applied migration. Local and production databases are separate.

## Source map

- `app/page.tsx`: interactive dashboard.
- `app/globals.css`: responsive layout and visual styles.
- `app/api/monitor/route.ts`: provider retrieval, classification, persistence and history API.
- `db/schema.ts` and `drizzle/`: database schema and migrations.
- `worker/index.ts`: server entrypoint.
- `.openai/hosting.json`: Sites project and database binding declaration.

## Hosting

The running application is hosted on **Sites**, not GitHub Pages. Its server-side feed retrieval and D1 history require a Worker backend. This repository is the source-code copy; pushing to GitHub does not automatically deploy changes to the existing Site. The background collection task is configured separately and is not recreated by cloning the repository.

No credentials, runtime databases, browser sessions, dependencies or generated build output are included.
