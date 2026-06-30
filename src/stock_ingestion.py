#%%
import pandas as pd
import yfinance as yf

#%%
tickers_path = './portfolio_products.txt'

with open(tickers_path, 'r') as f:
    lines = [l.strip() for l in f.readlines()]

sections = {}
current = None
for line in lines:
    if line.startswith('[') and line.endswith(']'):
        current = line[1:-1]
        sections[current] = []
    elif line and current:
        sections[current].append(line)

tickers = sections.get('STOCKS', [])

print(tickers)
#%%
df_prices = yf.download(
    tickers = tickers,
    auto_adjust = False,
    progress = False,
    period='2y',
    rounding=True
)["Close"]

df_prices = df_prices.stack().reset_index()

#%%
dict_renamed_columns = {
    "Date" : "base_date",
    "Ticker": "ticker",
    0 : "price"
}

df_prices.rename(columns=dict_renamed_columns, inplace=True)

df_prices.sort_values(["base_date"], inplace=True)

#%%
start_date = df_prices["base_date"].min()
end_date = df_prices["base_date"].max()

print(f"Start date: {start_date} / End date: {end_date}")

#%%
df_prices["return"] = df_prices.groupby("ticker")[["price"]].pct_change().round(4)

#%%
df_prices.to_csv('../data/stock_return.csv')
print('Stock Ingestion: Done')