import os
import shutil
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

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
    

def run_factor_residualization_option_a():
    price_path = "data/force1/prices_patched.csv"
    if not os.path.exists(price_path):
        raise FileNotFoundError(f"Missing {price_path}. Run price fetch first.")

    df = pd.read_csv(price_path, index_col=0, parse_dates=True)
    
    # 1. Calculate daily percentage returns
    rets = df[['MAGS', 'SMH', 'SPMO', 'VOO', 'QQQ']].pct_change().dropna()
    
    # 2. Equal-weighted target basket return
    rets['basket'] = rets[['MAGS', 'SMH', 'SPMO']].mean(axis=1)
    
    window = 60
    alphas = []
    betas_voo = []
    betas_qqq = []
    clean_residuals = []

    # 3. 60-day rolling OLS: Basket ~ VOO + QQQ (Clean control)
    for i in range(len(rets)):
        if i < window:
            alphas.append(np.nan)
            betas_voo.append(np.nan)
            betas_qqq.append(np.nan)
            clean_residuals.append(np.nan)
            continue
            
        sub = rets.iloc[i-window:i]
        Y = sub['basket']
        X = sm.add_constant(sub[['VOO', 'QQQ']])
        
        try:
            model = sm.OLS(Y, X).fit()
            a = model.params['const']
            b_voo = model.params['VOO']
            b_qqq = model.params['QQQ']
            
            # Out-of-sample 1-day clean residual
            pred_ret = a + b_voo * rets['VOO'].iloc[i] + b_qqq * rets['QQQ'].iloc[i]
            actual_ret = rets['basket'].iloc[i]
            res = actual_ret - pred_ret
            
            alphas.append(a)
            betas_voo.append(b_voo)
            betas_qqq.append(b_qqq)
            clean_residuals.append(res)
        except Exception:
            alphas.append(np.nan)
            betas_voo.append(np.nan)
            betas_qqq.append(np.nan)
            clean_residuals.append(np.nan)

    rets['alpha'] = alphas
    rets['beta_voo'] = betas_voo
    rets['beta_qqq'] = betas_qqq
    rets['factor_clean_resid'] = clean_residuals
    rets['cum_clean_resid'] = rets['factor_clean_resid'].cumsum()

    # 4. Calculate Annualized Information Ratio (IR) post-clean control
    clean_series = rets['factor_clean_resid'].dropna()
    ann_ir = (clean_series.mean() / clean_series.std()) * np.sqrt(252)

    # 5. Export to data/state/ and Drive destination data/force1/
    os.makedirs("data/state", exist_ok=True)
    os.makedirs("data/force1", exist_ok=True)
    os.makedirs("charts/force1", exist_ok=True)
    
    csv_state_path = "data/state/force1_factor_residualized.csv"
    csv_drive_path = "data/force1/force1_factor_residualized.csv"
    rets.to_csv(csv_state_path)
    shutil.copy(csv_state_path, csv_drive_path)

    # 6. Generate Clean Cumulative Residual Plot
    plt.figure(figsize=(10, 5))
    plt.plot(rets.index, rets['cum_clean_resid'], label=f"Option A Clean Residual (IR = {ann_ir:.3f})", color="navy")
    plt.title("Force 1: Factor-Cleaned Cumulative Residual (vs VOO + QQQ)")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Clean Residual Return")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    chart_path = "charts/force1/force1_clean_residual_option_a.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()

    print("=== Option A Factor Residualization Complete ===")
    print(f"Rolling 60d Mean Beta (VOO): {rets['beta_voo'].mean():.3f}")
    print(f"Rolling 60d Mean Beta (QQQ): {rets['beta_qqq'].mean():.3f}")
    print(f"Clean Annualized Information Ratio (IR): {ann_ir:.3f}")
    print(f"Artifacts synced to: {csv_drive_path} and {chart_path}")

if __name__ == "__main__":
    run_factor_residualization_option_a()