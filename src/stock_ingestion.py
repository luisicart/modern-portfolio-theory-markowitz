#%%
import pandas as pd
import yfinance as yf

#%%
tickers_path = '../portfolio_products.txt'
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