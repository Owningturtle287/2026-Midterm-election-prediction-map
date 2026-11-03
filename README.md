# Midterm Atlas · 2026

A complete interactive forecast of the 2026 U.S. House, Senate, and governor elections, reviewed at **November 3, 2026, 3:22 p.m. CST**.

**Favorite picks: House 236 D–199 R; Senate 51 D–47 R–2 Democratic-caucusing I; governors 29 D–21 R.** These are predictions, not results. Editorial probabilities are judgmental, not backtested model calibration. Senate expectations averaged across uncertain outcomes are closer to51–52 Democratic-aligned seats.

[Open the interactive atlas](https://owningturtle287.github.io/2026-Midterm-election-prediction-map/) · [Full analysis and all officeholders](docs/FORECAST.md) · [Complete 585-seat comparison CSV](docs/2026-midterm-comparison.csv)

The Election Day review retained all winners and totals. The earlier 5:55 check was in the morning; its prior p.m. label has been corrected. [Read the latest review](docs/FORECAST.md#election-day-review--322-pm-cst).

## Features

- Accurate geographic maps, with Alaska and Hawaii at lower left.
- Every 435 voting House district, every 35 Senate contest, all 50 governorships and the complete current 100-senator roster.
- State focus, district/candidate search, filters, zoom and pan, accessible race list, and responsive layouts.
- Current-versus-predicted officeholders, candidate portraits with individual sources and honest fallbacks, uncertainty ratings and race rationales.
- Shared polling-error slider; top cards preserve the original forecast while scenarios explore other outcomes.
- Source register and explicit exclusions for fabricated polling firms. Third-party baselines are not falsely described as a fully decontaminated clean-room poll aggregation.

Portrait coverage: **1,020 of 1,047 named candidates (97.4%)**, including every Senate candidate and every named predicted winner. The remaining 27 use labeled initials.

## GitHub Pages deployment

Pushes to `main` automatically run **Deploy GitHub Pages**. After the build and deployment finish, open the workflow run's **Summary**: the **github-pages** environment and the **Midterm Atlas is live** summary both contain the clickable site link. The workflow can also be started manually with **Run workflow**.

Pages must use **GitHub Actions** as its source in **Settings → Pages → Build and deployment**. The workflow uploads only `dist/`, after checking JavaScript and validating all forecast and map data.

## Run and verify

No build, npm installation, API key, or live data connection is needed. Serve `dist/` using any static web server. For example:

```sh
python -m http.server 8000 --directory dist
node --check dist/app.js
node scripts/validate.cjs
```

The application vendors D3 v7.9.0 and topojson-client 3.1.0 with their copyright notices. Fonts and candidate images are external; the site has system-font and initials fallbacks. Forecast and map data are committed snapshots.

## Data provenance

- Geography: Census TIGERweb Legislative layer 0 (120th Congress), with layer 4 (119th Congress) substituted for Missouri. See `dist/assets/geometry-provenance.json`.
- Current incumbents: official House Clerk XML/member/vacancy lists, official Senate directory, National Governors Association. Nonvoting delegates are excluded.
- House anchor: Call the Map November 2 district forecast; explicit narrow winner overrides in MI-10, PA-01, IA-03, FL-22. Primary polling and independent judgment check other contests.
- All forecast records, sources, rationales and current-member comparisons: `dist/assets/forecast.json`.
- LA-05 and LA-06: Republican party forecasts with eventual individual winners unresolved; November 3 all-party primaries can require December 12 runoffs.

The full methodology, limits, original-source links and tables are in [docs/FORECAST.md](docs/FORECAST.md). Current members in changed-map states are compared by district number; this is not an unchanged-geography swing calculation.
