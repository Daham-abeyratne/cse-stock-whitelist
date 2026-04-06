# CSE Stock Whitelist (Swing Trading Tracker)

A rule-based system that **tracks Colombo Stock Exchange (CSE) stocks daily** and maintains a **whitelist + candidates list** for swing trading analysis and Machine Learning data collection.

> ✅ This project **does NOT** generate “best trades” or buy/sell calls.  
> It only **filters and tracks** stocks based on consistent market activity and transparent, user-defined rules.

---

## What this system does

Once per day (automatically), the system:

1. **Fetches Activity:** Pulls the **Top 10 Most Active Trades** list from CSE (ranked by trade count, the primary retail interest indicator).
2. **Maintains Continuity:** Updates tracking records for:
   - The Top 10 stocks of the day.
   - Any stocks already in the active pipeline.
   - **20-Day Cooldown:** Churned stocks are monitored for **20 trading days** before being "frozen" to ensure mid-month recoveries are captured.
3. **Swing Evaluation:** Evaluates each stock using a **rolling 10-trading-day window** to identify momentum shifts and volatility trends.
4. **Point-in-Time Snapshots (ML Ready):** Every historical entry saves the stock's Score, Beta, CV, and Market Cap at that specific moment. This creates a high-fidelity dataset for future **Machine Learning** training without "look-ahead bias."
5. **Circular Lifecycle:** Stocks move dynamically between `Track`, `Candidate`, and `Whitelist`. If a `Churned` stock reappears in the Top 10, the system "resurrects" it back into the active cycle immediately.

---

## Data Sources (CSE)

The system uses publicly available CSE endpoints to fetch data such as:

- Trade count / Trade volume (from “Most Active Trades” list)
- Turnover & Share volume
- Day’s High / Low / Close
- Market Capitalization
- Beta vs ASPI (and S&P SL20 where applicable)

---

## Automation

This project runs **automatically once per day** at 12:02 UTC (17:32 Asia/Colombo) using **GitHub Actions**.

- **Scheduled runs:** Updates tracking, evaluates rules, and generates daily outputs.
- **Manual runs:** Supported via `workflow_dispatch`.

---

## Privacy & Ethical Note

This repository is public **for code transparency**, but:

✅ **All stored results and generated outputs are kept in a separate private repository.**

The private data repository contains:
- **`stocks/`**: Full historical JSON records (the evolving ML dataset).
- **`daily/`**: Daily snapshots of market activity.
- **`outputs/`**: The current Whitelist and Candidates files.

This public repo contains only the logic, pipeline code, and workflow configurations.

---

## High-Level Architecture

### 1. Code Repository (This Repo)
Contains the fetching logic, evaluation engine (`evaluator.py`), state transition rules, and GitHub Actions.

### 2. Data Repository (Private)
Acts as the persistent database. The GitHub Action clones this repo, runs the pipeline locally in the runner, and pushes the updated JSON state back to ensure data persistence across runs.

---

## What this is NOT

- ❌ **Not a trading bot:** It does not execute trades.
- ❌ **Not financial advice:** Thresholds (Beta, Market Cap, Score) are research parameters.
- ❌ **Not a prediction system:** It is a filtering pipeline that provides the structured data required to *eventually* build a prediction system.
- ❌ **Not “best stock” recommendations:** It only identifies stocks meeting specific liquidity and momentum criteria.

---

## Disclaimer

This is a **personal research project**. Stock market investments carry significant risk. Always verify data independently and consult with a certified financial advisor before making investment decisions.
