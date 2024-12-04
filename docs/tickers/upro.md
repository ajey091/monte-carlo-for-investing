---
layout: default
ticker: UPRO
---

{% assign ticker = page.ticker %}
{% assign params = site.data.parameters[ticker] %}
{% assign signal_data = site.data.signals.signals[ticker] %}

# {{ ticker }} Analysis

[← Back to Dashboard](../index.html)

## Current Status
- **Signal**: {{ signal_data.signal }}
- **Price**: ${{ signal_data.close_price }}
- **RSI**: {{ signal_data.rsi | round: 2 }}
- **Volatility**: {{ signal_data.volatility | round: 3 }}

## Charts
![Price and Moving Averages](../assets/images/{{ ticker }}_price_ma.png)
![RSI](../assets/images/{{ ticker }}_price_rsi.png)
![Volatility](../assets/images/{{ ticker }}_price_vol.png)

## Technical Indicators
- Short MA ({{ params.ma_short }} day): {{ signal_data.ma_short | round: 2 }}
- Long MA ({{ params.ma_long }} day): {{ signal_data.ma_long | round: 2 }}
- MA Cross Status: {{ signal_data.indicators.ma_cross }}
- RSI Status: {{ signal_data.indicators.rsi_status }}
- Volatility Status: {{ signal_data.indicators.volatility_status }}

## Strategy Parameters
- RSI Period: {{ params.rsi_period }}
- RSI Oversold: {{ params.rsi_oversold }}
- RSI Overbought: {{ params.rsi_overbought }}
- Volatility Window: {{ params.volatility_window }}
- Volatility Threshold: {{ params.volatility_threshold | round: 3 }}