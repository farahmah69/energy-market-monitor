from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import requests

URL = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU'
OUTPUT = Path(__file__).resolve().parent / 'output'


def main():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    if df.shape[1] != 2:
        raise ValueError('Unexpected FRED CSV structure')
    df.columns = ['Date', 'Price']
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = (df.dropna(subset=['Date', 'Price'])
            .drop_duplicates(subset='Date')
            .sort_values('Date').tail(365).reset_index(drop=True))
    if len(df) < 32:
        raise ValueError('Not enough valid observations for 30-period volatility')

    df['Daily_Return'] = df['Price'].pct_change() * 100
    df['MA_7'] = df['Price'].rolling(7).mean()
    df['MA_30'] = df['Price'].rolling(30).mean()
    df['Volatility_30'] = df['Daily_Return'].rolling(30).std()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT / 'brent_market_data.csv', index=False)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes[0, 0].plot(df['Date'], df['Price'], label='Brent Price')
    axes[0, 0].plot(df['Date'], df['MA_7'], label='MA 7')
    axes[0, 0].plot(df['Date'], df['MA_30'], label='MA 30')
    axes[0, 0].set_title('Brent Oil Price Trends')
    axes[0, 0].set_ylabel('USD per barrel')
    axes[0, 0].legend()
    axes[0, 1].plot(df['Date'], df['Daily_Return'])
    axes[0, 1].axhline(0, color='gray', linestyle='--')
    axes[0, 1].set_title('Returns Between Observations (%)')
    axes[1, 0].plot(df['Date'], df['Volatility_30'])
    axes[1, 0].set_title('30-Observation Return Volatility (%)')
    axes[1, 1].hist(df['Price'], bins=25, edgecolor='white')
    axes[1, 1].set_title('Brent Price Distribution')
    axes[1, 1].set_xlabel('USD per barrel')
    for ax in axes.flat:
        ax.grid(alpha=0.2)
    fig.suptitle('ENERGY MARKET INTELLIGENCE DASHBOARD', fontsize=18, fontweight='bold')
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(OUTPUT / 'energy_market_dashboard.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

    latest, previous = df.iloc[-1], df.iloc[-2]
    change = (latest['Price'] / previous['Price'] - 1) * 100
    trend = 'UPWARD' if latest['MA_7'] > latest['MA_30'] else 'DOWNWARD OR NEUTRAL'
    report = f'''ENERGY MARKET INTELLIGENCE REPORT
=================================
Generated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}
Latest published observation: {latest['Date']:%Y-%m-%d}
Brent price: ${latest['Price']:.2f} per barrel
Return vs previous observation: {change:+.2f}%
MA7: ${latest['MA_7']:.2f}
MA30: ${latest['MA_30']:.2f}
30-observation return volatility: {latest['Volatility_30']:.2f}%
Moving-average signal: {trend}

Data: FRED DCOILBRENTEU (EIA source). Moving averages use observations,
not calendar days. Volatility is not annualized.
Descriptive analysis only; not investment advice.
'''
    (OUTPUT / 'market_report.txt').write_text(report, encoding='utf-8')
    print(report)
    print(f'Outputs saved to: {OUTPUT}')


if __name__ == '__main__':
    main()
