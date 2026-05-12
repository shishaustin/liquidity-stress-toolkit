#!/usr/bin/env python3
"""
liquidity-stress-toolkit demo
Runs a full liquidity stress test across four scenarios + Monte Carlo deposit simulation.
Inputs represent a mid-size US bank (~$50B balance sheet).
"""
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from liquidity import run_all_scenarios, monte_carlo_deposit_stress, SCENARIOS

# ── Balance Sheet Inputs ($B) ─────────────────────────────────────
HQLA = 8.5
RETAIL_DEPOSITS = 28.0
WHOLESALE_FUNDING = 12.0
SECURED_BORROWING_CAPACITY = 6.0
COMMITTED_CREDIT_LINES = 5.5

print("=" * 65)
print("  Liquidity Stress Toolkit — Demo")
print("=" * 65)
print(f"\n  Firm profile (hypothetical ~$50B bank):")
print(f"    HQLA:                     ${HQLA}B")
print(f"    Retail Deposits:          ${RETAIL_DEPOSITS}B")
print(f"    Wholesale Funding:        ${WHOLESALE_FUNDING}B")
print(f"    Secured Borrowing Cap:    ${SECURED_BORROWING_CAPACITY}B")
print(f"    Committed Credit Lines:   ${COMMITTED_CREDIT_LINES}B")

# ── Stress Test ───────────────────────────────────────────────────
print("\n[1] Running stress tests across 4 scenarios (30-day horizon)...")
results = run_all_scenarios(
    HQLA, RETAIL_DEPOSITS, WHOLESALE_FUNDING,
    SECURED_BORROWING_CAPACITY, COMMITTED_CREDIT_LINES,
)

cols = ["scenario", "total_liquid_assets_bn", "total_outflows_bn",
        "net_liquidity_bn", "lcr_pct", "survival_horizon_days", "passes_30day_lcr"]
print(f"\n  {'Scenario':<26} {'HQLA+Secured':>13} {'Outflows':>10} {'Net Liq':>9} "
      f"{'LCR%':>7} {'Survival':>10} {'Pass?':>6}")
print("  " + "-" * 82)
for _, r in results.iterrows():
    flag = "✓" if r["passes_30day_lcr"] else "✗ FAIL"
    print(f"  {r['scenario']:<26} ${r['total_liquid_assets_bn']:>10.1f}B "
          f"${r['total_outflows_bn']:>7.1f}B ${r['net_liquidity_bn']:>6.1f}B "
          f"{r['lcr_pct']:>7.1f}% {r['survival_horizon_days']:>8.1f}d {flag:>6}")

# ── Monte Carlo ───────────────────────────────────────────────────
print("\n[2] Monte Carlo deposit stress simulation (10,000 paths)...")
mc = monte_carlo_deposit_stress(
    base_deposits_bn=RETAIL_DEPOSITS,
    mean_runoff_pct=0.08,
    std_runoff_pct=0.04,
    n_simulations=10_000,
)
print(f"    Mean runoff:       ${mc['mean_runoff_bn']:.2f}B")
print(f"    95th percentile:   ${mc['p95_runoff_bn']:.2f}B")
print(f"    99th percentile:   ${mc['p99_runoff_bn']:.2f}B")
print(f"    Prob runoff >10%:  {mc['prob_exceed_10pct_bn']:.1f}%")

# ── Charts ────────────────────────────────────────────────────────
print("\n[3] Generating charts...")
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Liquidity Stress Test Results", fontweight="bold")

scenarios_list = results["scenario"].tolist()
lcrs = results["lcr_pct"].tolist()
colors = ["#16a34a" if v >= 100 else "#dc2626" for v in lcrs]
axes[0].barh(scenarios_list, lcrs, color=colors, edgecolor="white")
axes[0].axvline(100, color="black", linestyle="--", linewidth=1.2, label="100% LCR minimum")
axes[0].set_title("LCR by Scenario")
axes[0].set_xlabel("LCR (%)")
axes[0].legend(fontsize=8)
axes[0].grid(axis="x", alpha=0.3)

rng = np.random.default_rng(42)
runoffs = RETAIL_DEPOSITS * np.clip(rng.normal(0.08, 0.04, 10_000), 0, 1)
axes[1].hist(runoffs, bins=60, color="#2563eb", alpha=0.7, edgecolor="white")
axes[1].axvline(np.percentile(runoffs, 95), color="#dc2626", linestyle="--", linewidth=1.5, label="P95")
axes[1].axvline(np.percentile(runoffs, 99), color="#7c3aed", linestyle="--", linewidth=1.5, label="P99")
axes[1].set_title("Deposit Runoff Distribution (Monte Carlo)")
axes[1].set_xlabel("Runoff ($B)")
axes[1].set_ylabel("Frequency")
axes[1].legend(fontsize=8)
axes[1].grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("liquidity_stress_results.png", dpi=150, bbox_inches="tight")
print("    Chart saved to: liquidity_stress_results.png")

print("\n[Done] Liquidity stress test complete.")
print("=" * 65)
