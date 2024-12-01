---
layout: default
---

# Trading Signals

{% assign signals = site.data.signals %}

## Current Signals ({{ signals.date }})

| Symbol | Signal | RSI | Volatility |
|--------|--------|-----|------------|
{% for symbol in signals.signals %}
| {{ symbol[0] }} | {{ symbol[1].signal }} | {{ symbol[1].rsi | round: 2 }} | {{ symbol[1].volatility | round: 3 }} |
{% endfor %}

## Strategy Parameters

{% assign params = site.data.parameters %}

### Moving Averages
- Short MA Period: {{ params.VOO.ma_short }}
- Long MA Period: {{ params.VOO.ma_long }}

### RSI Settings
- Period: {{ params.VOO.rsi_period }}
- Oversold Level: {{ params.VOO.rsi_oversold }}
- Overbought Level: {{ params.VOO.rsi_overbought }}

### Volatility
- Window: {{ params.VOO.volatility_window }}
- Threshold: {{ params.VOO.volatility_threshold | round: 3 }}

## Strategy Summary

{{ signals.summary }}