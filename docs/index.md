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

## Current Market Signals

{% for symbol in site.data.parameters %}
{% assign ticker = symbol[0] %}
{% assign params = symbol[1] %}
{% assign signal_data = site.data.signals.signals[ticker] %}

### {{ ticker }} Analysis

#### Charts
![Price and Moving Averages](./assets/images/{{ ticker }}_price_ma.png)
![RSI](./assets/images/{{ ticker }}_price_rsi.png)
![Volatility](./assets/images/{{ ticker }}_price_vol.png)

#### Current Status
- **Signal**: {{ signal_data.signal }}
- **Price**: ${{ signal_data.close_price }}
- **RSI**: {{ signal_data.rsi | round: 2 }}
- **Volatility**: {{ signal_data.volatility | round: 3 }}

#### Technical Indicators
- Short MA ({{ params.ma_short }} day): {{ signal_data.ma_short | round: 2 }}
- Long MA ({{ params.ma_long }} day): {{ signal_data.ma_long | round: 2 }}
- MA Cross Status: {{ signal_data.indicators.ma_cross }}
- RSI Status: {{ signal_data.indicators.rsi_status }}
- Volatility Status: {{ signal_data.indicators.volatility_status }}

#### Strategy Parameters
- RSI Period: {{ params.rsi_period }}
- RSI Oversold: {{ params.rsi_oversold }}
- RSI Overbought: {{ params.rsi_overbought }}
- Volatility Window: {{ params.volatility_window }}
- Volatility Threshold: {{ params.volatility_threshold | round: 3 }}

---

{% endfor %}



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

- Buy Signals: {{ buy_signals }}
- Sell Signals: {{ sell_signals }}
- Hold Signals: {{ hold_signals }}