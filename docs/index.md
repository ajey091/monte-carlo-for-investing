---
layout: default
---

# Trading Strategy Dashboard

## Strategy Summary

{{ site.data.signals.summary }}

## Current Market Signals

{% for symbol in site.data.parameters %}
{% assign ticker = symbol[0] %}
{% assign params = symbol[1] %}
{% assign signal_data = site.data.signals.signals[ticker] %}

### {{ ticker }} Analysis

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