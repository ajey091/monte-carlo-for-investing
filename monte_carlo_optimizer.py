import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class MonteCarloBacktester:
    def __init__(self, symbols: List[str], start_date: str, end_date: str = None):
        """
        Initialize the backtester with symbols and date range.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to today)
        """
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date if end_date else datetime.now().strftime('%Y-%m-%d')
        self.data = self._fetch_data()
        
    def _fetch_data(self) -> pd.DataFrame:
        """Fetch data for all symbols and combine into one DataFrame."""
        data = {}
        for symbol in self.symbols:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=self.start_date, end=self.end_date)
            data[symbol] = df['Close']
        return pd.DataFrame(data)
    
    def generate_random_strategy(self) -> Dict:
        """Generate random strategy parameters."""
        return {
            'ma_short': np.random.randint(3, 50),
            'ma_long': np.random.randint(51, 200),
            'rsi_period': np.random.randint(5, 30),
            'rsi_oversold': np.random.randint(20, 40),
            'rsi_overbought': np.random.randint(60, 80),
            'volatility_window': np.random.randint(10, 60),
            'volatility_threshold': np.random.uniform(1.0, 3.0)
        }
    
    def calculate_signals(self, symbol: str, params: Dict) -> pd.Series:
        """Calculate trading signals based on strategy parameters."""
        df = self.data[symbol].to_frame()
        
        # Calculate technical indicators
        df['MA_short'] = df[symbol].rolling(window=params['ma_short']).mean()
        df['MA_long'] = df[symbol].rolling(window=params['ma_long']).mean()
        
        # RSI calculation
        delta = df[symbol].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=params['rsi_period']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatility calculation
        df['Volatility'] = df[symbol].pct_change().rolling(params['volatility_window']).std()
        
        # Generate signals (1 for buy, -1 for sell, 0 for hold)
        signals = pd.Series(0, index=df.index)
        
        # Buy conditions
        buy_condition = (
            (df['MA_short'] > df['MA_long']) & 
            (df['RSI'] < params['rsi_oversold']) &
            (df['Volatility'] < params['volatility_threshold'])
        )
        
        # Sell conditions
        sell_condition = (
            (df['MA_short'] < df['MA_long']) & 
            (df['RSI'] > params['rsi_overbought']) |
            (df['Volatility'] > params['volatility_threshold'] * 1.5)
        )
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals.fillna(0)
    
    def backtest_strategy(self, symbol: str, signals: pd.Series) -> Dict:
        """Run backtest for a single symbol with given signals."""
        prices = self.data[symbol]
        position = 0
        trades = []
        
        for date in signals.index:
            if signals[date] == 1 and position == 0:  # Buy signal
                position = 1
                trades.append({
                    'type': 'buy',
                    'date': date,
                    'price': prices[date]
                })
            elif signals[date] == -1 and position == 1:  # Sell signal
                position = 0
                trades.append({
                    'type': 'sell',
                    'date': date,
                    'price': prices[date]
                })
        
        if not trades:
            return {'total_return': 0, 'num_trades': 0, 'sharpe_ratio': 0}
        
        # Calculate returns
        returns = []
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades):
                returns.append(trades[i+1]['price'] / trades[i]['price'] - 1)
        
        if not returns:
            return {'total_return': 0, 'num_trades': 0, 'sharpe_ratio': 0}
        
        total_return = np.prod([1 + r for r in returns]) - 1
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0
        
        return {
            'total_return': total_return,
            'num_trades': len(trades),
            'sharpe_ratio': sharpe_ratio,
            'trades': trades
        }
    
    def run_monte_carlo(self, num_simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation for all symbols."""
        results = {symbol: [] for symbol in self.symbols}
        best_strategies = {symbol: None for symbol in self.symbols}
        
        for _ in range(num_simulations):
            strategy_params = self.generate_random_strategy()
            
            for symbol in self.symbols:
                signals = self.calculate_signals(symbol, strategy_params)
                backtest_results = self.backtest_strategy(symbol, signals)
                
                if backtest_results['total_return'] > 0:  # Only store profitable strategies
                    results[symbol].append({
                        'params': strategy_params,
                        'results': backtest_results
                    })
                    
                    # Update best strategy if current one is better
                    if (not best_strategies[symbol] or 
                        backtest_results['total_return'] > best_strategies[symbol]['results']['total_return']):
                        best_strategies[symbol] = {
                            'params': strategy_params,
                            'results': backtest_results
                        }
        
        return {
            'best_strategies': best_strategies,
            'all_results': results
        }

    def plot_best_strategy(self, symbol: str, strategy_results: Dict):
        """Plot the performance of the best strategy for a given symbol."""
        if not strategy_results['trades']:
            print(f"No trades found for {symbol}")
            return
        
        plt.figure(figsize=(15, 7))
        plt.plot(self.data[symbol], label='Price', alpha=0.5)
        
        # Plot buy and sell points
        buy_dates = [t['date'] for t in strategy_results['trades'] if t['type'] == 'buy']
        buy_prices = [t['price'] for t in strategy_results['trades'] if t['type'] == 'buy']
        sell_dates = [t['date'] for t in strategy_results['trades'] if t['type'] == 'sell']
        sell_prices = [t['price'] for t in strategy_results['trades'] if t['type'] == 'sell']
        
        plt.scatter(buy_dates, buy_prices, color='green', marker='^', label='Buy', s=100)
        plt.scatter(sell_dates, sell_prices, color='red', marker='v', label='Sell', s=100)
        
        plt.title(f'Best Strategy Performance for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    # Initialize backtester
    symbols = ['VOO', 'SSO', 'UPRO', 'QQQ', 'QLD', 'TQQQ', 'SOXL']
    start_date = '2010-01-01'
    
    backtester = MonteCarloBacktester(symbols, start_date)
    
    # Run Monte Carlo simulation
    results = backtester.run_monte_carlo(num_simulations=1000)
    
    # Print results for each symbol
    for symbol in symbols:
        best_strategy = results['best_strategies'][symbol]
        if best_strategy:
            print(f"\nBest strategy for {symbol}:")
            print(f"Total Return: {best_strategy['results']['total_return']*100:.2f}%")
            print(f"Number of Trades: {best_strategy['results']['num_trades']}")
            print(f"Sharpe Ratio: {best_strategy['results']['sharpe_ratio']:.2f}")
            print("\nStrategy Parameters:")
            for param, value in best_strategy['params'].items():
                print(f"{param}: {value}")
            
            # Plot the results
            backtester.plot_best_strategy(symbol, best_strategy['results'])