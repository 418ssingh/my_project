import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================
# STEP 1: GET DATA
# ============================================
def get_stock_data(symbol="RELIANCE.NS", years=3):
    """Download stock data using yfinance"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    return df

# ============================================
# STEP 2: CREATE FEATURES
# ============================================
def create_features(df):
    """Create technical indicators - bulletproof version"""
    df = df.copy()
    
    # Ensure all columns are 1D Series
    for col in df.columns:
        if isinstance(df[col], pd.DataFrame):
            df[col] = df[col].iloc[:, 0]
        elif isinstance(df[col], np.ndarray) and df[col].ndim > 1:
            df[col] = pd.Series(df[col].ravel(), index=df.index)
    
    # Basic returns
    df['returns_1d'] = df['Close'].pct_change()
    df['returns_5d'] = df['Close'].pct_change(5)
    df['returns_20d'] = df['Close'].pct_change(20)
    
    # Simple moving averages
    df['sma_20'] = df['Close'].rolling(20).mean()
    if isinstance(df['sma_20'], pd.DataFrame):
        df['sma_20'] = df['sma_20'].iloc[:, 0]
    
    df['sma_50'] = df['Close'].rolling(50).mean()
    if isinstance(df['sma_50'], pd.DataFrame):
        df['sma_50'] = df['sma_50'].iloc[:, 0]
    
    # Volatility
    df['volatility'] = df['returns_1d'].rolling(20).std()
    if isinstance(df['volatility'], pd.DataFrame):
        df['volatility'] = df['volatility'].iloc[:, 0]
    
    # Volume features
    df['volume_sma'] = df['Volume'].rolling(20).mean()
    if isinstance(df['volume_sma'], pd.DataFrame):
        df['volume_sma'] = df['volume_sma'].iloc[:, 0]
    
    # Use .values to avoid DataFrame issues
    volume_vals = df['Volume'].values.ravel()
    volume_sma_vals = df['volume_sma'].values.ravel()
    df['volume_ratio'] = volume_vals / volume_sma_vals
    
    # Price vs SMA
    close_vals = df['Close'].values.ravel()
    sma20_vals = df['sma_20'].values.ravel()
    sma50_vals = df['sma_50'].values.ravel()
    
    df['price_vs_sma20'] = close_vals / sma20_vals - 1
    df['price_vs_sma50'] = close_vals / sma50_vals - 1
    
    # Drop NaN
    df = df.dropna()
    
    return df

# ============================================
# STEP 3: CREATE TARGET
# ============================================
def create_target(df):
    """Create binary target: 1 if next day price up, 0 if down"""
    df = df.copy()
    
    # Debug info
    print(f"Data range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"Total days: {len(df)}")
    
    df['next_day_return'] = df['Close'].shift(-1) / df['Close'] - 1
    df['target'] = (df['next_day_return'] > 0).astype(int)
    
    # Remove last row (no target)
    df = df.dropna()
    
    # Debug target distribution
    target_counts = df['target'].value_counts()
    print(f"Target distribution: Up days: {target_counts.get(1, 0)}, Down days: {target_counts.get(0, 0)}")
    print(f"Up day probability: {target_counts.get(1, 0)/len(df):.2%}")
    
    return df

# ============================================
# STEP 4: TRAIN MODEL (PROPER WALK-FORWARD)
# ============================================
def train_model(df, feature_cols):
    """Train Random Forest with PROPER train/test split"""
    
    # Prepare data
    X = df[feature_cols]
    y = df['target']
    
    # Use 70% for training, 30% for testing (chronological)
    split_idx = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"\n📅 Training period: {df.index[0].strftime('%Y-%m-%d')} to {df.index[split_idx-1].strftime('%Y-%m-%d')}")
    print(f"📅 Testing period: {df.index[split_idx].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Predict on TEST data only!
    y_pred = model.predict(X_test)
    
    # Calculate metrics on test data
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    
    print(f"✅ Test Accuracy: {accuracy:.2%}")
    print(f"✅ Test Precision: {precision:.2%}")
    
    return model, accuracy, precision, X_test.index, y_test, y_pred

# ============================================
# STEP 5: BACKTEST STRATEGY
# ============================================
def backtest_strategy(df, model, feature_cols, test_indices):
    """Simulate trading ONLY on test period"""
    df = df.copy()
    
    # Get predictions only for test period
    X_test = df.loc[test_indices, feature_cols]
    df.loc[test_indices, 'prediction'] = model.predict(X_test)
    
    # Trading logic
    df['position'] = df['prediction'].shift(1)
    df['returns'] = df['Close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    
    # Calculate cumulative returns only for test period
    test_df = df.loc[test_indices].copy()
    test_df['cumulative_market'] = (1 + test_df['returns']).cumprod()
    test_df['cumulative_strategy'] = (1 + test_df['strategy_returns']).cumprod()
    
    return test_df

# ============================================
# STEP 6: PLOT RESULTS
# ============================================
def plot_results(df, symbol):
    """Plot strategy vs buy & hold"""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['cumulative_market'], 
             label='Buy & Hold', linewidth=2, color='blue')
    plt.plot(df.index, df['cumulative_strategy'], 
             label='ML Strategy', linewidth=2, color='green')
    plt.title(f'{symbol} - ML Trading Strategy (Test Period Only)')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    print("🚀 Starting ML Trading Strategy (NO LOOK-AHEAD BIAS)...")
    
    # List of stocks to test
    symbols = ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS"]
    
    results_summary = []
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"📊 TESTING: {symbol}")
        print(f"{'='*60}")
        
        # Get data
        df = get_stock_data(symbol)
        
        if len(df) < 200:  # Need enough data
            print(f"⚠️ Not enough data for {symbol}, skipping...")
            continue
        
        # Create features
        print("🔧 Creating technical features...")
        df_features = create_features(df)
        
        # Create target
        df_with_target = create_target(df_features)
        
        # Define feature columns
        feature_cols = ['returns_1d', 'returns_5d', 'returns_20d', 
                        'sma_20', 'sma_50', 'volatility', 
                        'volume_ratio', 'price_vs_sma20', 'price_vs_sma50']
        
        # Train model (with proper split)
        print("\n🤖 Training Random Forest model...")
        model, accuracy, precision, test_indices, y_test, y_pred = train_model(
            df_with_target, feature_cols
        )
        
        # Backtest on test period only
        print("\n📈 Running backtest on test period...")
        results = backtest_strategy(df_with_target, model, feature_cols, test_indices)
        
        # Calculate returns
        market_return = results['cumulative_market'].iloc[-1] - 1
        strategy_return = results['cumulative_strategy'].iloc[-1] - 1
        excess_return = strategy_return - market_return
        
        # Calculate win rate
        win_rate = (results['strategy_returns'] > 0).mean()
        
        # Store results
        results_summary.append({
            'Symbol': symbol,
            'Accuracy': f"{accuracy:.2%}",
            'Win Rate': f"{win_rate:.2%}",
            'Market Return': f"{market_return:.2%}",
            'Strategy Return': f"{strategy_return:.2%}",
            'Excess Return': f"{excess_return:.2%}"
        })
        
        print(f"\n📊 {symbol} PERFORMANCE (TEST PERIOD ONLY)")
        print(f"{'='*40}")
        print(f"Buy & Hold Return: {market_return:.2%}")
        print(f"ML Strategy Return: {strategy_return:.2%}")
        print(f"Excess Return: {excess_return:.2%}")
        print(f"Strategy Win Rate: {win_rate:.2%}")
        
        # Plot for first stock
        if symbol == symbols[0]:
            plot_results(results, symbol)
    
    # Print summary table
    print(f"\n{'='*70}")
    print("📊 FINAL SUMMARY - ALL STOCKS (TEST PERIOD ONLY)")
    print(f"{'='*70}")
    summary_df = pd.DataFrame(results_summary)
    print(summary_df.to_string(index=False))
    
    # Calculate average excess return
    if len(results_summary) > 0:
        avg_excess = summary_df['Excess Return'].str.rstrip('%').astype(float).mean()
        print(f"\n📈 Average Excess Return: {avg_excess:.2f}%")
        print(f"📈 Average Accuracy: {summary_df['Accuracy'].str.rstrip('%').astype(float).mean():.2f}%")

if __name__ == "__main__":
    main()