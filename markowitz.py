#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bcb import sgs
from pypfopt import EfficientFrontier

np.random.seed(22)

MAX_WEIGHT_PER_ASSET = 0.20

#%%
with open('./portfolio_products.txt', 'r') as f:
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
SELECTED_BONDS = [
    tuple(l.split(',', 1))
    for l in sections.get('BONDS', [])
]

print(f"Stocks  : {tickers}")
print(f"Bonds   : {SELECTED_BONDS}")

#%%
df_stock_return = pd.read_csv('./data/stock_return.csv', index_col=0)
df_stock_return.rename(columns={'ticker': 'product'}, inplace=True)
df_stock_return['base_date'] = pd.to_datetime(df_stock_return['base_date'])
df_stock_return['type'] = 'stock'

df_stock_return = df_stock_return[df_stock_return['product'].isin(tickers)]

stock_min = df_stock_return['base_date'].min()
stock_max = df_stock_return['base_date'].max()

#%%
df_bond_raw = pd.read_csv('./data/treasure_return.csv', index_col=0)
df_bond_raw['base_date'] = pd.to_datetime(df_bond_raw['base_date'])
df_bond_raw['due_date']  = pd.to_datetime(df_bond_raw['due_date'])

mask = pd.Series(False, index=df_bond_raw.index)
for bond_type, maturity in SELECTED_BONDS:
    mask |= (
        (df_bond_raw['treasure_type'] == bond_type) &
        (df_bond_raw['due_date'] == maturity)
    )

df_bond_return = (
    df_bond_raw[mask &
                (df_bond_raw['base_date'] >= stock_min) &
                (df_bond_raw['base_date'] <= stock_max)]
    .copy()
    .reset_index(drop=True)
)

df_bond_return['product'] = (
    df_bond_return['treasure_type'].str.replace(' ', '_') + '_' +
    df_bond_return['due_date'].dt.strftime('%Y-%m-%d')
)
df_bond_return['type'] = 'bond'
df_bond_return.rename(columns={'morn_sell_unit_price': 'price'}, inplace=True)
df_bond_return = df_bond_return[['base_date', 'product', 'price', 'return', 'type']]

#%%
df_return = pd.concat([df_stock_return, df_bond_return], ignore_index=True).dropna(subset=['return'])

df_pivot = (
    df_return
    .pivot_table(index='base_date', columns='product', values='return')
    .sort_index()
    .dropna(axis=1, how='all')
    .dropna()
)

print(f"Assets in portfolio : {list(df_pivot.columns)}")
print(f"Period              : {df_pivot.index.min().date()}  ->  {df_pivot.index.max().date()}")
print(f"Shape               : {df_pivot.shape}")

#%%
selic_data = sgs.get({'selic': 432}, last=1)
rf_annual  = selic_data['selic'].max() / 100
print(f"Risk-free rate (SELIC): {rf_annual:.2%}")

#%%
TRADING_DAYS = 252

mu = df_pivot.mean() * TRADING_DAYS
S  = df_pivot.cov()  * TRADING_DAYS
annual_vol = np.sqrt(np.diag(S))

#%%
ef_min = EfficientFrontier(mu, S, weight_bounds=(0, 1))
ef_min.min_volatility()
w_min = ef_min.clean_weights()
ret_min, vol_min, sharpe_min = ef_min.portfolio_performance(risk_free_rate=rf_annual)

weights_min = (
    pd.DataFrame.from_dict(w_min, orient='index', columns=['Weight'])
    .query('Weight > 0')
)

print("\n-- Minimum Risk Portfolio --")
print(weights_min.round(4).to_string())
print(f"Return: {ret_min:.2%}  |  Volatility: {vol_min:.2%}  |  Sharpe: {sharpe_min:.4f}")

#%%
ef_tan = EfficientFrontier(mu, S, weight_bounds=(0, 1))
ef_tan.max_sharpe(risk_free_rate=rf_annual)
w_tan = ef_tan.clean_weights()
ret_tan, vol_tan, sharpe_tan = ef_tan.portfolio_performance(risk_free_rate=rf_annual)

weights_tan = (
    pd.DataFrame.from_dict(w_tan, orient='index', columns=['Weight'])
    .query('Weight > 0')
)

print("\n-- Tangent Portfolio (Max. Sharpe) --")
print(weights_tan.round(4).to_string())
print(f"Return: {ret_tan:.2%}  |  Volatility: {vol_tan:.2%}  |  Sharpe: {sharpe_tan:.4f}")

#%%
min_feasible_weight = round(1 / len(mu), 2)

if MAX_WEIGHT_PER_ASSET < min_feasible_weight:
    print(f"\n-- Diversified Tangent Portfolio --")
    print(f"MAX_WEIGHT_PER_ASSET ({MAX_WEIGHT_PER_ASSET:.0%}) is infeasible with {len(mu)} assets.")
    print(f"Minimum required to allocate 100%: {min_feasible_weight:.0%}")
    print(f"Suggestion: set MAX_WEIGHT_PER_ASSET >= {min_feasible_weight:.0%}")
    ret_tan_div, vol_tan_div, sharpe_tan_div = ret_tan, vol_tan, sharpe_tan
    weights_tan_div = weights_tan
else:
    try:
        ef_tan_div = EfficientFrontier(mu, S, weight_bounds=(0, MAX_WEIGHT_PER_ASSET))
        ef_tan_div.max_sharpe(risk_free_rate=rf_annual)
        w_tan_div = ef_tan_div.clean_weights()
        ret_tan_div, vol_tan_div, sharpe_tan_div = ef_tan_div.portfolio_performance(risk_free_rate=rf_annual)
        weights_tan_div = (
            pd.DataFrame.from_dict(w_tan_div, orient='index', columns=['Weight'])
            .query('Weight > 0')
        )
        print(f"\n-- Diversified Tangent Portfolio (max. {MAX_WEIGHT_PER_ASSET:.0%} per asset) --")
        print(weights_tan_div.round(4).to_string())
        print(f"Return: {ret_tan_div:.2%}  |  Volatility: {vol_tan_div:.2%}  |  Sharpe: {sharpe_tan_div:.4f}")
    except Exception:
        print(f"\n-- Diversified Tangent Portfolio --")
        print(f"Optimization infeasible with MAX_WEIGHT_PER_ASSET={MAX_WEIGHT_PER_ASSET:.0%}.")
        print(f"The optimizer could not find a portfolio with positive Sharpe under these constraints.")
        print(f"Try increasing MAX_WEIGHT_PER_ASSET or adding more assets with positive expected return.")
        ret_tan_div, vol_tan_div, sharpe_tan_div = ret_tan, vol_tan, sharpe_tan
        weights_tan_div = weights_tan

#%%
target_rets = np.linspace(ret_min, mu.max(), 60)
frontier_rets, frontier_vols = [], []

for tr in target_rets:
    ef = EfficientFrontier(mu, S, weight_bounds=(0, 1))
    try:
        ef.efficient_return(target_return=tr)
        r, v, _ = ef.portfolio_performance(risk_free_rate=rf_annual)
        frontier_rets.append(r)
        frontier_vols.append(v)
    except Exception:
        pass

frontier_rets = np.array(frontier_rets)
frontier_vols = np.array(frontier_vols)

frontier_div_rets, frontier_div_vols = [], []

for tr in target_rets:
    ef = EfficientFrontier(mu, S, weight_bounds=(0, MAX_WEIGHT_PER_ASSET))
    try:
        ef.efficient_return(target_return=tr)
        r, v, _ = ef.portfolio_performance(risk_free_rate=rf_annual)
        frontier_div_rets.append(r)
        frontier_div_vols.append(v)
    except Exception:
        pass

frontier_div_rets = np.array(frontier_div_rets)
frontier_div_vols = np.array(frontier_div_vols)

#%%
n_assets = len(mu)
W        = np.random.dirichlet(np.ones(n_assets), size=3000)
rets_mc  = W @ mu.values
vols_mc  = np.sqrt(np.einsum('ij,jk,ik->i', W, S.values, W))

w_eq   = np.repeat(1 / n_assets, n_assets)
ret_eq = float(w_eq @ mu.values)
vol_eq = float(np.sqrt(w_eq @ S.values @ w_eq))

#%%
def short_label(name):
    return name.replace('Tesouro_', 'TD_').replace('Aposentadoria_Extra_', '').replace('.SA', '')

labels = [short_label(c) for c in mu.index]

fig, ax = plt.subplots(figsize=(12, 7.5))

ax.scatter(vols_mc, rets_mc, alpha=0.18, s=7, label="Portfolios (Monte Carlo)")
ax.plot(frontier_vols, frontier_rets, lw=1.8, color='navy', ls='--', alpha=0.5, label="Unconstrained Frontier")
ax.plot(frontier_div_vols, frontier_div_rets, lw=2.2, color='navy', label=f"Diversified Frontier (max. {MAX_WEIGHT_PER_ASSET:.0%})")

cml_vols = np.linspace(0, max(frontier_div_vols) * 1.1, 100)
cml_rets = rf_annual + ((ret_tan_div - rf_annual) / vol_tan_div) * cml_vols
ax.plot(cml_vols, cml_rets, lw=1.4, ls='--', color='gray', label="CML")

ax.scatter(vol_min,     ret_min,     marker='*', s=280, zorder=5, label="Minimum Risk")
ax.scatter(vol_tan,     ret_tan,     marker='X', s=170, zorder=5, label="Tangent (Max. Sharpe)")
ax.scatter(vol_tan_div, ret_tan_div, marker='P', s=170, zorder=5, label=f"Diversified Tangent (max. {MAX_WEIGHT_PER_ASSET:.0%})")
ax.scatter(vol_eq,      ret_eq,      marker='o', s=110, zorder=5, label="Equal Weights")

ax.scatter(annual_vol, mu.values, marker='D', s=70, zorder=5, label="Assets")
for i, lbl in enumerate(labels):
    ax.annotate(lbl, (annual_vol[i], mu.values[i]),
                xytext=(6, 6), textcoords='offset points', fontsize=7.5)

ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
ax.set_title("Markowitz Efficient Frontier — Personal Portfolio (Stocks + Government Bonds)")
ax.set_xlabel("Annual Volatility")
ax.set_ylabel("Expected Annual Return")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('./img/efficient_frontier.png', dpi=150)
plt.show()

#%%
print("\n================================================")
print("  PERSONAL PORTFOLIO SUMMARY")
print("================================================")
print(f"Risk-free rate (SELIC) : {rf_annual:.2%}")
print(f"Period                 : {df_pivot.index.min().date()}  ->  {df_pivot.index.max().date()}")
print(f"Number of assets       : {n_assets}")

print("\n-- Minimum Risk Portfolio --")
print(weights_min.round(4).to_string())
print(f"Return: {ret_min:.2%}  |  Volatility: {vol_min:.2%}  |  Sharpe: {sharpe_min:.3f}")

print("\n-- Tangent Portfolio (Max. Sharpe) --")
print(weights_tan.round(4).to_string())
print(f"Return: {ret_tan:.2%}  |  Volatility: {vol_tan:.2%}  |  Sharpe: {sharpe_tan:.3f}")

print(f"\n-- Diversified Tangent Portfolio (max. {MAX_WEIGHT_PER_ASSET:.0%} per asset) --")
print(weights_tan_div.round(4).to_string())
print(f"Return: {ret_tan_div:.2%}  |  Volatility: {vol_tan_div:.2%}  |  Sharpe: {sharpe_tan_div:.3f}")

print("\n-- Equal Weights (benchmark) --")
print(pd.DataFrame({'Weight': np.round(w_eq, 4)}, index=mu.index).to_string())
print(f"Return: {ret_eq:.2%}  |  Volatility: {vol_eq:.2%}")