#%%
import pandas as pd

TREASURE_URL = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/"
TREASURE_ARC = "precotaxatesourodireto.csv"

TREASURE_PATH = f"{TREASURE_URL}/{TREASURE_ARC}"

#%%

df = pd.read_csv(
    TREASURE_PATH,
    sep=";",
    decimal=",",
    encoding="latin1"
)

#%%

renamed_columns = {
    'Tipo Titulo': 'treasure_type', 
    'Data Vencimento': 'due_date', 
    'Data Base': 'base_date', 
    'Taxa Compra Manha': 'morn_buy_rate',
    'Taxa Venda Manha': 'morn_sell_rate', 
    'PU Compra Manha': 'morn_buy_unit_price', 
    'PU Venda Manha': 'morn_sell_unit_price',
    'PU Base Manha': 'morn_base_unit_price'
}

df.rename(
    columns=renamed_columns,
    inplace=True
)

#%%
df["due_date"] = pd.to_datetime(df["due_date"],dayfirst=True)
df["base_date"] = pd.to_datetime(df["base_date"],dayfirst=True)

#%%
df.sort_values(
    ["treasure_type", "due_date", "base_date"],
    inplace=True
)

df["return"] = df.groupby(["treasure_type", "due_date"])["morn_sell_unit_price"].pct_change().round(4)

#%%
df.to_csv("../data/treasure_return.csv")
print("Treasure Ingestion: Done")