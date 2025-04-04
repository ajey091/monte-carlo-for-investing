# strategy_monitor.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from openai import OpenAI
from typing import Dict, List, Any
from monte_carlo_optimizer import MonteCarloBacktester
from dotenv import load_dotenv
load_dotenv()
import matplotlib.pyplot as plt
from io import BytesIO

class StrategyMonitor:
    def __init__(self, symbols: List[str], params_file: str = 'best_parameters.json'):
        """
        Initialize the strategy monitor
        """
        self.symbols = symbols
        self.params_file = params_file
        self.best_params = self._load_parameters()
        self.optimizer = MonteCarloBacktester(symbols, start_date='2010-01-01')
        
    # Add this new method
    def optimize_parameters(self, force: bool = False):
        """
        Run Monte Carlo optimization if:
        1. No parameters exist
        2. It's been a week since last optimization
        3. force=True
        """
        should_optimize = force
        
        if not os.path.exists(self.params_file):
            should_optimize = True
        else:
            last_modified = os.path.getmtime(self.params_file)
            days_since_update = (datetime.now() - datetime.fromtimestamp(last_modified)).days
            if days_since_update >= 7:  # Weekly optimization
                should_optimize = True
        
        if should_optimize:
            print("Running Monte Carlo optimization...")
            results = self.optimizer.run_monte_carlo(num_simulations=1000)
            
            new_params = {}
            for symbol in self.symbols:
                if symbol in results['best_strategies']:
                    new_params[symbol] = results['best_strategies'][symbol]['params']
                    
            # Compare with existing parameters
            current_params = self._load_parameters()
            for symbol in new_params:
                if symbol in current_params:
                    if (new_params[symbol]['total_return'] > 
                        current_params[symbol].get('total_return', 0)):
                        current_params[symbol] = new_params[symbol]
                else:
                    current_params[symbol] = new_params[symbol]
            
            self._save_parameters(current_params)
            
            return new_params
        return None
        
    def _load_parameters(self) -> Dict:
        """Load best parameters from JSON file"""
        if os.path.exists(self.params_file):
            with open(self.params_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_parameters(self, params: Dict):
        """Save best parameters to JSON file"""
        with open(self.params_file, 'w') as f:
            json.dump(params, f, indent=4)

    def get_current_signals(self) -> Dict[str, Dict]:
        """
        Calculate current trading signals for all symbols
        """
        signals = {}
        for symbol in self.symbols:
            try:
                # Fetch recent data
                ticker = yf.Ticker(symbol)
                df = ticker.history(start='2010-01-01', interval='1d')  
                
                if symbol in self.best_params:
                    params = self.best_params[symbol]
                    signal = self._calculate_signal(symbol, df, params)  # Pass symbol here
                    signals[symbol] = signal
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                signals[symbol] = {"error": str(e)}
        
        return signals

    def _calculate_signal(self, symbol: str, df: pd.DataFrame, params: Dict) -> Dict:
        """
        Calculate trading signals based on stored parameters
        """
        # Calculate indicators
        close = df['Close']
        
        # Moving averages
        ma_short = close.rolling(window=params['ma_short']).mean()
        ma_long = close.rolling(window=params['ma_long']).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Volatility
        volatility = close.pct_change().rolling(params['volatility_window']).std()
        
        # Get latest values
        current_ma_short = ma_short.iloc[-1]
        current_ma_long = ma_long.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_volatility = volatility.iloc[-1]
        
        # Save indicators to dataframe for plotting
        df['RSI'] = rsi
        df['Volatility'] = volatility
        
        # Determine signal
        signal = "HOLD"
        if (current_ma_short > current_ma_long and 
            current_rsi < params['rsi_oversold'] and 
            current_volatility < params['volatility_threshold']):
            signal = "BUY"
        elif (current_ma_short < current_ma_long or 
            current_rsi > params['rsi_overbought'] or 
            current_volatility > params['volatility_threshold'] * 1.5):
            signal = "SELL"
        
        # Generate plots
        plots = self._generate_plots(symbol, df, params)
        
        return {
            "date": df.index[-1].strftime('%Y-%m-%d'),
            "signal": signal,
            "close_price": close.iloc[-1],
            "ma_short": current_ma_short,
            "ma_long": current_ma_long,
            "rsi": current_rsi,
            "volatility": current_volatility,
            "indicators": {
                "ma_cross": "BULLISH" if current_ma_short > current_ma_long else "BEARISH",
                "rsi_status": "OVERSOLD" if current_rsi < params['rsi_oversold'] else 
                            "OVERBOUGHT" if current_rsi > params['rsi_overbought'] else "NEUTRAL",
                "volatility_status": "HIGH" if current_volatility > params['volatility_threshold'] else "LOW"
            },
            "plots": plots
        }
    
    def _generate_plots(self, symbol: str, df: pd.DataFrame, params: Dict) -> Dict[str, str]:
        """
        Generate plots for price/MA, RSI, and volatility
        Returns base64 encoded strings of the plots
        """
        plots_dir = Path('docs/assets/images')
        plots_dir.mkdir(exist_ok=True, parents=True)
        
        # Price and MA plot
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Price', alpha=0.7)
        plt.plot(df.index, df['Close'].rolling(window=params['ma_short']).mean(), 
                label=f'{params["ma_short"]}d MA', alpha=0.8)
        plt.plot(df.index, df['Close'].rolling(window=params['ma_long']).mean(), 
                label=f'{params["ma_long"]}d MA', alpha=0.8)
        plt.title(f'{symbol} Price and Moving Averages')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / f'{symbol}_price_ma.png')
        plt.close()
        
        # RSI plot
        plt.figure(figsize=(12, 4))
        plt.plot(df.index, df['RSI'], label='RSI', color='blue')
        plt.axhline(y=params['rsi_oversold'], color='green', linestyle='--', label='Oversold')
        plt.axhline(y=params['rsi_overbought'], color='red', linestyle='--', label='Overbought')
        plt.title(f'{symbol} RSI')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / f'{symbol}_price_rsi.png')
        plt.close()
        
        # Volatility plot
        plt.figure(figsize=(12, 4))
        plt.plot(df.index, df['Volatility'], label='Volatility', color='purple')
        # plt.axhline(y=params['volatility_threshold'], color='red', linestyle='--', label='Threshold')
        plt.title(f'{symbol} Volatility')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / f'{symbol}_price_vol.png')
        plt.close()
        
        return

    def generate_summary(self, signals: Dict[str, Dict], api_key: str) -> str:
        """
        Generate a summary of current signals using OpenAI
        """
        client = OpenAI(api_key=api_key)
        # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Prepare the prompt
        prompt = f"""
        Analyze the following trading signals and provide a clear, concise summary of the current market situation 
        and recommended actions. Include specific insights about leveraged ETFs if relevant.
        
        Current Signals:
        {json.dumps(signals, indent=2)}
        
        Please provide:
        1. Overall market sentiment
        2. Specific recommendations for each ETF
        3. Risk warnings if applicable
        4. Key levels to watch
        """
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading analyst focusing on ETFs and leveraged ETFs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o-mini",  # or whichever model you prefer
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def save_daily_signals(self, signals: Dict[str, Dict], summary: str):
        """
        Save daily signals and summary to a file
        """
        date = datetime.now().strftime('%Y-%m-%d')
        output_dir = Path('daily_signals')
        output_dir.mkdir(exist_ok=True)
        
        output = {
            "date": date,
            "signals": signals,
            "summary": summary
        }
        
        with open(output_dir / f'signals_{date}.json', 'w') as f:
            json.dump(output, f, indent=4)

def main():
    symbols = ['VOO', 'SSO', 'UPRO', 'QQQ', 'QLD', 'TQQQ', 'SOXL']
    
    monitor = StrategyMonitor(symbols)
    
    # Run optimization if needed
    monitor.optimize_parameters()
    
    # Get current signals
    signals = monitor.get_current_signals()
    
    # Generate summary (replace with your OpenAI API key)
    summary = monitor.generate_summary(signals, os.getenv('OPENAI_API_KEY'))
    
    # Save daily results
    monitor.save_daily_signals(signals, summary)
    
if __name__ == "__main__":
    main()