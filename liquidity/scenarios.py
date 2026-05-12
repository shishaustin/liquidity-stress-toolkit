import numpy as np
from dataclasses import dataclass


@dataclass
class StressScenario:
    name: str
    retail_deposit_runoff_pct: float
    wholesale_runoff_pct: float
    secured_funding_haircut_pct: float
    contingent_draw_pct: float
    hqla_haircut_pct: float
    description: str = ""


SCENARIOS = {
    "idiosyncratic": StressScenario(
        name="Idiosyncratic Stress",
        retail_deposit_runoff_pct=0.10,
        wholesale_runoff_pct=0.50,
        secured_funding_haircut_pct=0.25,
        contingent_draw_pct=0.30,
        hqla_haircut_pct=0.00,
        description="Firm-specific stress (ratings downgrade, operational event).",
    ),
    "market_wide": StressScenario(
        name="Market-Wide Stress",
        retail_deposit_runoff_pct=0.05,
        wholesale_runoff_pct=0.25,
        secured_funding_haircut_pct=0.40,
        contingent_draw_pct=0.20,
        hqla_haircut_pct=0.05,
        description="Systemic market dislocation (2008-style).",
    ),
    "combined": StressScenario(
        name="Combined Stress",
        retail_deposit_runoff_pct=0.15,
        wholesale_runoff_pct=0.75,
        secured_funding_haircut_pct=0.50,
        contingent_draw_pct=0.50,
        hqla_haircut_pct=0.10,
        description="Simultaneous idiosyncratic + market stress.",
    ),
    "severe": StressScenario(
        name="Severe / Tail Stress",
        retail_deposit_runoff_pct=0.25,
        wholesale_runoff_pct=0.90,
        secured_funding_haircut_pct=0.70,
        contingent_draw_pct=0.75,
        hqla_haircut_pct=0.15,
        description="Extreme tail event — SVB/2023-style bank run dynamics.",
    ),
}
