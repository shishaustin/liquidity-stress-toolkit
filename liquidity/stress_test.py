import numpy as np
import pandas as pd
from .scenarios import StressScenario, SCENARIOS


def run_stress_test(
    hqla_bn: float,
    retail_deposits_bn: float,
    wholesale_funding_bn: float,
    secured_borrowing_capacity_bn: float,
    committed_credit_lines_bn: float,
    scenario: StressScenario,
    days: int = 30,
) -> dict:
    """
    Run a single liquidity stress test over a given horizon.
    Returns cash outflows, inflows, net liquidity position, and LCR.
    """
    # Stressed outflows
    retail_runoff = retail_deposits_bn * scenario.retail_deposit_runoff_pct
    wholesale_runoff = wholesale_funding_bn * scenario.wholesale_runoff_pct
    contingent_draws = committed_credit_lines_bn * scenario.contingent_draw_pct
    total_outflows = retail_runoff + wholesale_runoff + contingent_draws

    # Stressed inflows / liquidity buffer
    stressed_hqla = hqla_bn * (1 - scenario.hqla_haircut_pct)
    available_secured = secured_borrowing_capacity_bn * (1 - scenario.secured_funding_haircut_pct)
    total_liquid_assets = stressed_hqla + available_secured

    # LCR (simplified)
    lcr = (total_liquid_assets / total_outflows) * 100 if total_outflows > 0 else float("inf")

    # Survival horizon: days until liquidity exhausted assuming linear daily draw
    daily_net_outflow = total_outflows / days
    survival_days = total_liquid_assets / daily_net_outflow if daily_net_outflow > 0 else float("inf")

    return {
        "scenario": scenario.name,
        "stressed_hqla_bn": round(stressed_hqla, 2),
        "available_secured_bn": round(available_secured, 2),
        "total_liquid_assets_bn": round(total_liquid_assets, 2),
        "retail_runoff_bn": round(retail_runoff, 2),
        "wholesale_runoff_bn": round(wholesale_runoff, 2),
        "contingent_draws_bn": round(contingent_draws, 2),
        "total_outflows_bn": round(total_outflows, 2),
        "net_liquidity_bn": round(total_liquid_assets - total_outflows, 2),
        "lcr_pct": round(lcr, 1),
        "survival_horizon_days": round(survival_days, 1),
        "passes_30day_lcr": lcr >= 100,
    }


def monte_carlo_deposit_stress(
    base_deposits_bn: float,
    mean_runoff_pct: float,
    std_runoff_pct: float,
    n_simulations: int = 10000,
    seed: int = 42,
) -> dict:
    """Monte Carlo simulation of deposit runoff uncertainty."""
    rng = np.random.default_rng(seed)
    runoff_pcts = np.clip(rng.normal(mean_runoff_pct, std_runoff_pct, n_simulations), 0, 1)
    runoffs_bn = base_deposits_bn * runoff_pcts
    return {
        "mean_runoff_bn": round(float(runoffs_bn.mean()), 2),
        "p95_runoff_bn": round(float(np.percentile(runoffs_bn, 95)), 2),
        "p99_runoff_bn": round(float(np.percentile(runoffs_bn, 99)), 2),
        "std_bn": round(float(runoffs_bn.std()), 2),
        "prob_exceed_10pct_bn": round(float((runoffs_bn > base_deposits_bn * 0.10).mean() * 100), 1),
    }


def run_all_scenarios(
    hqla_bn, retail_deposits_bn, wholesale_funding_bn,
    secured_borrowing_capacity_bn, committed_credit_lines_bn, days=30
) -> pd.DataFrame:
    results = []
    for key, scenario in SCENARIOS.items():
        r = run_stress_test(
            hqla_bn, retail_deposits_bn, wholesale_funding_bn,
            secured_borrowing_capacity_bn, committed_credit_lines_bn,
            scenario, days,
        )
        results.append(r)
    return pd.DataFrame(results)
