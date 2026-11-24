# Ehdreon

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?logo=numpy&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version%20Control-F05032?logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![Focus](https://img.shields.io/badge/Focus-Quantitative%20Research-blue)

**Reproducible quantitative research infrastructure for designing, backtesting and validating systematic trading strategies.**

Ehdreon is an evolving quantitative research platform built to turn investment hypotheses into controlled, traceable and reproducible experiments.

The project currently focuses on building a reliable research foundation before introducing more advanced strategy families, machine learning, portfolio construction, risk management or live execution.

> **Current stage:** Quantitative Research Foundation  
> **Primary focus:** Reproducible strategy research and temporal validation  
> **Status:** Active development

---

## Why Ehdreon?

Backtesting a strategy is easy.

Building a research process where you can reliably answer:

- What exactly was tested?
- Which dataset was used?
- Which version of the strategy generated the result?
- Were future observations accidentally used?
- Were transaction costs included?
- Which period was used for selection?
- Can the experiment be reproduced later?
- Is an improvement real or simply the result of overfitting?

is much harder.

Ehdreon is being built around those questions.

The objective is not simply to create trading signals, but to build a disciplined quantitative research infrastructure capable of supporting increasingly sophisticated strategies and models.

---

## Current Capabilities

### Market Data

Ehdreon currently works with local historical OHLCV snapshots.

The data pipeline includes:

- Local CSV snapshots
- Datetime index reconstruction
- SHA-256 integrity verification
- Dataset metadata
- Required-column validation
- Finite numerical value validation
- Positive-price validation
- Non-negative volume validation
- OHLC consistency checks
- Duplicate and chronological-order checks

Research runs therefore depend on stable, identifiable datasets rather than downloading potentially different market data during every execution.

---

### Strategy Layer

The first implemented strategy family is a simple moving-average trend-following strategy.

Current implementation:

```text
sma_trend
version: 1
```

The strategy:

- calculates fast and slow moving averages from closing prices;
- enters a long state when the fast SMA is above the slow SMA;
- remains in cash otherwise;
- treats the warm-up period and equal averages as no-position states.

Different SMA windows represent different configurations of the same strategy implementation.

A minimal **Strategy Registry** is already available to identify strategies by name and version and associate them with their executable implementation.

---

## Backtesting Engine

The current engine simulates:

```text
Single asset
Daily frequency
Long / Cash
Fractional units
Explicit transaction costs
```

The temporal execution convention is:

```text
Signal generated after Close(t)
            ↓
Position executed at Open(t+1)
            ↓
Portfolio evolves using subsequent market prices
```

This separation is fundamental to prevent the strategy from acting on information before it would have been available.

---

## Execution Accounting

Ehdreon uses explicit portfolio accounting rather than applying simplified strategy-return adjustments.

The engine tracks:

- cash;
- asset quantity;
- execution price;
- transaction fees;
- portfolio equity;
- entries;
- exits;
- open positions.

When entering a position, transaction costs are included when determining the number of units that can be purchased.

```python
quantity = cash / (price * (1 + commission_rate))
```

Portfolio equity is then derived from the actual portfolio state:

```python
equity = cash + quantity * open_price
```

Transaction costs are therefore reflected through cash accounting and are not deducted twice from returns.

An open position is not automatically liquidated at the end of an evaluation period. Its market value remains part of portfolio equity even when it does not yet appear as a closed trade.

---

## Metrics

The current research engine calculates portfolio and strategy metrics including:

- Initial capital
- Final capital
- CAGR
- Annualized return
- Annualized volatility
- Sharpe ratio
- Maximum drawdown
- Drawdown date
- Positive active-return days
- Negative active-return days
- Exposure
- Order count

Trade-level analysis additionally records:

- Entry date
- Exit date
- Entry price
- Exit price
- Quantity
- Fees
- Gross PnL
- Net PnL
- Return
- Trade duration

Special cases such as no trades, cash-only periods, open positions and one-sided return distributions are explicitly handled.

---

## Benchmarks

Strategies are evaluated alongside Buy & Hold benchmarks.

The current benchmark implementation supports:

- Open-to-open Buy & Hold
- Gross benchmark
- Entry-cost-adjusted benchmark

This allows strategy performance to be compared against a simple passive alternative using accounting conventions compatible with the research engine.

---

## Experiment Configuration

Experiments use a validated and immutable configuration object.

The configuration defines research conditions such as:

- Initial capital
- Transaction costs
- Dataset
- Strategy
- Strategy parameters
- Temporal boundaries
- Evaluation mode

Invalid configurations are rejected before an experiment is executed.

This helps guarantee that experiment conditions remain explicit and stable throughout a run.

---

## Temporal Research Protocol

Ehdreon currently separates historical data into:

```text
TRAIN
VALIDATION
TEST
```

The current development protocol uses:

```text
TRAIN       → research and diagnostics
VALIDATION  → candidate comparison and selection
TEST        → isolated historical evaluation
```

Candidate strategies are **not selected using TEST performance**.

In development mode, TEST observations are excluded before strategy calculations are performed.

Historical observations before an evaluation period may still be used when required to calculate indicators or establish execution context, but they are not included in the metrics of the evaluated period.

Each evaluation period starts with independent capital.

---

## Experiment Runner

The experiment runner separates experiment computation from file loading, output presentation and persistence.

A simplified flow is:

```text
Experiment Configuration
        ↓
Validated Market Snapshot
        ↓
Data Preparation
        ↓
Strategy Signals
        ↓
Temporal Split
        ↓
Backtest
        ↓
Portfolio Accounting
        ↓
Metrics + Trades
        ↓
Benchmarks
        ↓
Structured Results
```

This architecture makes the research engine easier to test, reuse and extend.

---

## Experiment Records

Each persisted experiment contains information such as:

- Unique experiment identifier
- UTC creation timestamp
- Experiment configuration
- Dataset metadata
- Dataset hash
- Strategy metadata
- Code state
- Environment information
- Research conventions
- Evaluation results

Experiment records are stored as JSON.

The serialization layer explicitly distinguishes between:

```text
finite values
unavailable values
positive infinity
negative infinity
```

Unexpected `NaN` values are rejected instead of silently being written into experiment records.

Experiment files are created without overwriting previous experiments.

---

## Current Research Study

The current development branch focuses on a controlled SMA candidate comparison.

Four parameter configurations are being studied:

| Candidate | Fast SMA | Slow SMA |
|---|---:|---:|
| A | 20 | 100 |
| B | 50 | 100 |
| C | 20 | 200 |
| D | 50 | 200 |

The study follows a predefined research protocol:

```text
Protocol: sma_windows_v1
Evaluation mode: development
Selection period: VALIDATION
Primary ranking metric: Validation Sharpe
Transaction costs: included
```

Candidate comparison currently supports:

- explicit candidate definitions;
- validation-only ranking;
- descending Sharpe ranking;
- competition ranking for exact ties;
- explicit unavailable states;
- compatibility checks between experiment records;
- preservation of all candidate attempts.

The current objective is **not to identify an optimal SMA strategy**.

The objective is to build and verify a reproducible process for comparing strategy candidates under controlled conditions.

---

## Reproducibility

Current reproducibility mechanisms include:

- Stable local market snapshots
- SHA-256 dataset hashes
- Dataset metadata
- Immutable experiment configuration
- Git version tracking
- Recorded repository state
- Python version information
- Dependency files
- Versioned research conventions
- Experiment UUIDs
- UTC timestamps
- Persistent experiment results
- Non-overwriting experiment storage

---

## Testing

The project includes executable checks covering important components of the research pipeline.

Current tests include areas such as:

- Dataset integrity
- OHLCV validation
- Experiment configuration
- SMA calculation
- SMA warm-up behavior
- Future-data isolation
- Execution accounting
- Transaction costs
- Portfolio reconciliation
- Open positions
- Closed trades
- Cash-only scenarios
- Portfolio metrics
- Buy & Hold benchmarks
- Temporal splits
- Execution context
- TEST isolation
- Serialization
- Experiment persistence
- Strategy Registry
- Candidate generation
- Candidate ranking
- Ranking ties
- Missing metric states
- Experiment compatibility

---

## Architecture

```text
                         EHDREON
                            │
            ┌───────────────┴───────────────┐
            │                               │
           DATA                          CONFIG
            │                               │
            └───────────────┬───────────────┘
                            ↓
                       STRATEGIES
                            │
                            ↓
                     EXPERIMENT RUNNER
                            │
                 ┌──────────┴──────────┐
                 │                     │
             BACKTEST              BENCHMARKS
                 │                     │
                 └──────────┬──────────┘
                            ↓
                         METRICS
                            │
                            ↓
                    EXPERIMENT RECORD
                            │
                            ↓
                     RESEARCH LAYER
                            │
                CANDIDATES / RANKING
```

Current repository responsibilities are divided approximately into:

```text
src/
├── data/          # market data loading, validation and integrity
├── strategies/    # strategy implementations and registry
├── backtesting/   # execution, accounting and benchmarks
├── experiments/   # experiment execution, records and serialization
├── research/      # splits, candidates, ranking and comparison
├── metrics.py
├── trades.py
└── config.py
```

---

## Current Limitations

Ehdreon is still an early-stage research system.

The following components are **not implemented yet**:

- Full walk-forward analysis
- Statistical significance testing
- Multiple-testing controls
- Parameter stability analysis
- Advanced robustness testing
- Additional strategy families
- Machine learning models
- Feature engineering pipeline
- Multi-asset portfolios
- Portfolio optimization
- Position sizing framework
- Volatility targeting
- Independent Risk Engine
- Advanced slippage/liquidity modelling
- Paper trading
- Live trading
- Broker integration
- Production execution infrastructure
- Web application
- Public API
- AI Research Agent

Therefore, current backtest results should be interpreted as research evidence, **not as proof of persistent trading alpha**.

---

## Roadmap

### Current

**Reproducible SMA Candidate Study**

Complete the first end-to-end controlled research study:

```text
Candidates
    ↓
Protocol Validation
    ↓
Experiment Execution
    ↓
Persistence
    ↓
Compatibility Validation
    ↓
Validation Ranking
    ↓
Research Interpretation
```

### Next

**Strategy Validation**

- Parameter stability
- Sensitivity analysis
- Repeated temporal evaluation
- Basic walk-forward methodology
- Stronger robustness analysis

### Later

**Strategy Expansion**

- Momentum
- Mean reversion
- Additional trend models
- Statistical strategies

**Machine Learning**

- Feature pipelines
- Logistic regression baseline
- Tree-based models
- Probability calibration
- Temporal ML validation

**Portfolio & Risk**

- Multi-strategy portfolios
- Multi-asset portfolios
- Position sizing
- Volatility targeting
- Portfolio optimization
- Global risk controls

**Deployment**

- Paper trading
- Broker integration
- Controlled live execution

**AI Research**

- AI-assisted hypothesis generation
- Automated experiment preparation
- Research comparison
- Evidence synthesis

---

## Long-Term Vision

The long-term objective is for Ehdreon to evolve into an **AI-native quantitative research and portfolio infrastructure platform**.

The intended architecture separates:

```text
Research / Models
        ↓
Forecasts / Signals
        ↓
Portfolio Engine
        ↓
Risk Engine
        ↓
Execution Engine
        ↓
Broker
```

Models will generate forecasts, probabilities or signals.

They will **not directly control orders**.

Portfolio construction, risk management and execution will remain independent layers.

---

## Project Philosophy

Ehdreon is built around four principles:

**Reproducibility**  
Every important research result should be traceable to its data, configuration, code and conventions.

**Temporal correctness**  
Future information must not influence past decisions.

**Validation before complexity**  
Advanced models are only useful when the underlying research process is trustworthy.

**Evidence over backtest aesthetics**  
A high historical return, Sharpe ratio or win rate is not sufficient evidence of a persistent edge.

---

## Development Status

```text
Foundation               ████████████████░░░░
Research Infrastructure  ███████████████░░░░░
Strategy Validation      ██████░░░░░░░░░░░░░░
Strategy Diversity       ██░░░░░░░░░░░░░░░░░░
Machine Learning         ░░░░░░░░░░░░░░░░░░░░
Portfolio & Risk         ░░░░░░░░░░░░░░░░░░░░
Paper / Live             ░░░░░░░░░░░░░░░░░░░░
AI Research Platform     ░░░░░░░░░░░░░░░░░░░░
```

---

## Disclaimer

Ehdreon is currently a research and educational software project.

Nothing in this repository constitutes investment advice, and historical backtest performance does not guarantee future results.
