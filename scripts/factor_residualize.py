import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

def run_factor_residualization():
    path = "data/force1/prices_patched.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Run price fetch first.")
        
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    rets = df[['MAGS', 'SMH', 'SPMO', 'VOO']].pct_change().dropna()
    
    basket_ret = rets[['MAGS', 'SMH', 'SPMO']].mean(axis=1)
    rets['basket'] = basket_ret
    
    window = 60
    alphas = []
    betas_voo = []
    betas_spmo = []
    clean_residuals = []
    
    # 60-day rolling OLS regression: basket ~ VOO + SPMO
    for i in range(len(rets)):
        if i < window:
            alphas.append(np.nan)
            betas_voo.append(np.nan)
            betas_spmo.append(np.nan)
            clean_residuals.append(np.nan)
            continue
            
        sub = rets.iloc[i-window:i]
        Y = sub['basket']
        X = sm.add_constant(sub[['VOO', 'SPMO']])
        
        try:
            model = sm.OLS(Y, X).fit()
            a = model.params['const']
            b_voo = model.params['VOO']
            b_spmo = model.params['SPMO']
            
            # Out-of-sample 1-day residual calculation at time t
            curr_x = [1.0, rets['VOO'].iloc[i], rets['SPMO'].iloc[i]]
            pred_ret = a + b_voo * curr_x[1] + b_spmo * curr_x[2]
            actual_ret = rets['basket'].iloc[i]
            res = actual_ret - pred_ret
            
            alphas.append(a)
            betas_voo.append(b_voo)
            betas_spmo.append(b_spmo)
            clean_residuals.append(res)
        except Exception:
            alphas.append(np.nan)
            betas_voo.append(np.nan)
            betas_spmo.append(np.nan)
            clean_residuals.append(np.nan)
            
    rets['alpha'] = alphas
    rets['beta_voo'] = betas_voo
    rets['beta_spmo'] = betas_spmo
    rets['factor_clean_resid'] = clean_residuals
    rets['cum_clean_resid'] = rets['factor_clean_resid'].cumsum()
    
    # Calculate Sharpe / Information Ratio of clean residual
    clean_series = rets['factor_clean_resid'].dropna()
    ann_ir = (clean_series.mean() / clean_series.std()) * np.sqrt(252)
    
    os.makedirs("data/state", exist_ok=True)
    rets.to_csv("data/state/force1_factor_residualized.csv")
    
    print(f"=== Factor Residualization Complete ===")
    print(f"Rolling 60d Mean Beta VOO: {rets['beta_voo'].mean():.3f}")
    print(f"Rolling 60d Mean Beta SPMO: {rets['beta_spmo'].mean():.3f}")
    print(f"Factor-Cleaned Annualized Information Ratio (IR): {ann_ir:.3f}")
    
if __name__ == "__main__":
    run_factor_residualization()