#%%
import pandas as pd
import yfinance as yf

#%%
tickers_path = '../data/tickers.txt'
tickers = []

with open(tickers_path, 'r') as file:
    tickers = file.read().splitlines()

print(tickers)
#%%
df_prices = yf.download(
    tickers = tickers,
    auto_adjust = False,
    progress = False,
    period='6mo',
    rounding=True
)["Close"]

#%%
df_prices.head()
#%%
start_date = df_prices.index.min()
end_date = df_prices.index.max()

print(f"Start date: {start_date} / End date: {end_date}")

#%%
df_returns = df_prices.pct_change().round(4)

df_financial_returns = pd.merge(
    df_prices, 
    df_returns, 
    how='left', 
    left_index=True, 
    right_index=True,
    suffixes=['_price', '_return'])

#%%
df_financial_returns.to_csv('../data/financial_returns.csv')
print('Ingestion: Done')