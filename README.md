# CSE Stock Whitelist (Swing Trading Tracker)

A rule based system that **tracks CSE stocks daily** and maintains a **whitelist + candidates list** for swing trading analysis.

> ✅ This project **does NOT** generate “best trades” or buy/sell calls.  
> It only **filters and tracks** stocks based on consistent market activity and simple, transparent rules.

---

## What this system does

Once per day (automatically), the system:

1. Fetches the **Top 10 Most Active Trades** list from CSE (ranked by **trade count**, not turnover)
2. Updates tracking records for:
   - the Top 10 stocks of the day, and
   - any stocks already being tracked (until they are churned by hard rules)
3. Evaluates each tracked stock using a **rolling 7 trading day window**  
   (weekends and holidays are excluded)
4. Produces:
   - **Whitelist** (stocks that pass the rules)
   - **Candidates** (close to passing / still under observation)
   - **Per stock history/state** used to keep continuity across days

---

## Data sources (CSE)

The system uses publicly available CSE endpoints to fetch data such as:

- Trade count / trade volume (from “Most Active Trades” list)
- Turnover
- Share volume
- Day’s high / low
- Last traded / close-like price values available from the API
- Market capitalization
- Beta vs ASPI
- Beta vs S&P SL20

> Note: CSE’s “Most Active Trades” list is based on **trade count**, not turnover.

---

## Automation (runs once per day)

This project is designed to run **automatically once per day** (typically after market activity) using **GitHub Actions**.

- Manual runs are supported (`workflow_dispatch`)
- Scheduled runs update tracking + outputs

---

## Privacy & ethical note (IMPORTANT)

This repository is public **for code transparency**, but:

✅ **All stored results and generated outputs are kept in a separate private repository**  
for privacy and ethical reasons.

That private repo contains:
- historical tracking data (`stocks/`)
- daily snapshots (`daily/`)
- generated outputs (`outputs/`)

This public repo contains:
- only the code + workflow configuration
- no personal/private tracking datasets

---

## High-level architecture

### Code repository (this repo)
Contains:
- fetching logic
- tracking & evaluation rules
- CLI runner
- GitHub Actions workflow

### Data repository (private)
Contains:
- persisted tracking state (JSON files)
- daily snapshots
- current outputs (whitelist/candidates)

The automation flow:
1. GitHub Actions runs on schedule
2. It pulls the latest state from the private repo
3. Runs the pipeline
4. Pushes updated JSON state + outputs back to the private repo

---

## What this is NOT

- ❌ Not a trading bot  
- ❌ Not financial advice  
- ❌ Not a prediction system  
- ❌ Not “best stock” recommendations  

This project is **only a tracking and filtering pipeline** based on objective market activity rules.

---

## Disclaimer

This is a **personal project** created for learning and research purposes.

Always verify data independently and make financial decisions responsibly.
