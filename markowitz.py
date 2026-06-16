#%%
import pandas as pd
import numpy as np
from bcb import sgs

np.random.seed(22)

#%%
df_stock_return = pd.read_csv('./data/stock_return.csv', index_col=0)
stock_column_names = {
    'ticker': 'product'
}

df_stock_return.rename(columns=stock_column_names, inplace=True)

df_stock_return['type'] = 'stock'

#%%
df_treasure_return = pd.read_csv('./data/treasure_return.csv', index_col=0).reset_index(drop=True)
treasure_column_names = {
    'morn_sell_unit_price': 'price'
}

df_treasure_return['product'] = df_treasure_return['treasure_type'].astype(str) + '_' + df_treasure_return['due_date'].astype(str)
df_treasure_return['type'] = 'treasure'

df_treasure_return.rename(columns={'morn_sell_unit_price': 'price'}, inplace=True)

df_treasure_return.drop(columns=[
    'treasure_type',
    'due_date',
    'morn_buy_rate',
    'morn_sell_rate',
    'morn_buy_unit_price',
    'morn_base_unit_price'
    ], inplace=True)

df_treasure_return = df_treasure_return[['base_date','product', 'price', 'return', 'type']]
#%%
df_return = pd.concat([df_stock_return, df_treasure_return], ignore_index=True).dropna()

#%%
selic_code = {'selic': 432}
selic_data = sgs.get(selic_code, last=1)

ref_annual = selic_data['selic'].max()

print(ref_annual)
