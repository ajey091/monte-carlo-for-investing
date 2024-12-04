---
layout: default
---

# Trading Strategy Dashboard

## Project Overview

This project leverages Monte Carlo simulation to optimize trading strategies for ETFs and their leveraged variants. Using market data from 2010 to present, we identify optimal parameters for technical indicators and their combinations.

### Methodology
The Monte Carlo simulation evaluates parameter combinations across key technical indicators:

Moving average crossovers for trend identification
RSI for momentum and reversal signals
Volatility metrics for risk management

Our optimization framework targets three core objectives:

Return maximization with controlled drawdown exposure
Precise market entry and exit timing
Mitigation of leveraged ETF decay effects

### Strategy Components
- **Moving Average Crossover**: Uses optimized periods of 47/57 days for trend identification
- **RSI Boundaries**: Asymmetric bounds (38/77) for better risk management
- **Volatility Filters**: Adaptive thresholds to protect against market turbulence
- **Daily Monitoring**: Continuous signal generation and parameter optimization

### Implementation
- Weekly parameter optimization through Monte Carlo simulation
- Daily signal generation and market analysis
- Special risk management for leveraged instruments (2x and 3x ETFs)
- Automated monitoring and signal generation

## Strategy Summary

{{ site.data.signals.summary }}

## Quick Navigation

### S&P 500 ETFs
- [VOO - Vanguard S&P 500 ETF](./tickers/voo.html)
- [SSO - ProShares Ultra S&P 500 (2x)](./tickers/sso.html)
- [UPRO - ProShares UltraPro S&P 500 (3x)](./tickers/upro.html)

### NASDAQ ETFs
- [QQQ - Invesco QQQ Trust](./tickers/qqq.html)
- [QLD - ProShares Ultra QQQ (2x)](./tickers/qld.html)
- [TQQQ - ProShares UltraPro QQQ (3x)](./tickers/tqqq.html)

### Sector ETFs
- [SOXL - Direxion Daily Semiconductor Bull 3X](./tickers/soxl.html)

## Market Overview

{% assign buy_signals = 0 %}
{% assign sell_signals = 0 %}
{% assign hold_signals = 0 %}
{% for signal in site.data.signals.signals %}
  {% if signal[1].signal == 'BUY' %}
    {% assign buy_signals = buy_signals | plus: 1 %}
  {% elsif signal[1].signal == 'SELL' %}
    {% assign sell_signals = sell_signals | plus: 1 %}
  {% else %}
    {% assign hold_signals = hold_signals | plus: 1 %}
  {% endif %}
{% endfor %}

### Current Signal Distribution
- Buy Signals: {{ buy_signals }}
- Sell Signals: {{ sell_signals }}
- Hold Signals: {{ hold_signals }}