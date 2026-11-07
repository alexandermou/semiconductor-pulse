# Semiconductor Pulse

An English, mobile-friendly semiconductor market dashboard tracking **SOXL, NVDA, AMD, INTC, MU and QCOM**.

[Open the GitHub Pages dashboard](https://alexandermou.github.io/semiconductor-pulse/)

[Original Sites version](https://semiconductor-pulse-mou.alexandermou2000.chatgpt.site)

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

The public GitHub Pages version is served from **https://alexandermou.github.io/semiconductor-pulse/**. It uses the prebuilt browser assets in `docs/`. The `.github/workflows/pages.yml` workflow collects public quotes and news and publishes a Pages artifact on pushes, manual runs and a five-minute target schedule. GitHub scheduling and deployment can be delayed. The browser checks the latest published JSON every minute; this is separate from provider quote timestamps and the data collection schedule.

`pages/collect.py` uses Python standard libraries and no API keys. It retains provider errors, last-known values and timestamps when sources fail, merges previous published headlines, and carries forward the latest 500 historical observations for up to 30 days. Historical continuity depends on access to the previous published artifact. No private Sites credentials or API keys are embedded in the public page.

`pages/Dashboard.tsx` is the Pages frontend, and `pages/entry.tsx` is its entrypoint. To regenerate `docs/app.js`, install the project dependencies and `esbuild`, then run `node pages/build.mjs`. The workflow publishes the checked-in compiled assets; frontend edits require rebuilding those assets. To refresh a local snapshot, run `python3 pages/collect.py`.

The original server-backed app remains hosted on Sites, using Cloudflare Workers and D1. GitHub Pages is a separate static deployment and does not change the existing Sites database or its background task. Neither deployment executes trading orders.

No credentials, runtime databases, browser sessions or installed dependencies are included in this repository.
