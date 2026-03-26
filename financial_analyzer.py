"""
Financial data loader and metrics calculator.
Loads financial_data.csv and computes Revenue Growth, Operating Margin, Net Margin.
"""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class YearlyMetrics:
    year: int
    revenue: int
    cogs: int
    operating_expenses: int
    net_income: int
    operating_income: int
    revenue_growth: Optional[float]   # % vs previous year, None for first year
    operating_margin: float           # % of revenue
    net_margin: float                 # % of revenue


def load_and_calculate(csv_path: str = "financial_data.csv") -> list[YearlyMetrics]:
    """Load CSV and return list of YearlyMetrics sorted by year."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")

    rows: list[dict] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: int(v) for k, v in row.items()})

    rows.sort(key=lambda r: r["year"])

    metrics: list[YearlyMetrics] = []
    for i, row in enumerate(rows):
        revenue = row["revenue"]
        cogs = row["cogs"]
        op_expenses = row["operating_expenses"]
        net_income = row["net_income"]
        operating_income = revenue - cogs - op_expenses

        if i == 0:
            revenue_growth = None
        else:
            prev_revenue = rows[i - 1]["revenue"]
            revenue_growth = (revenue - prev_revenue) / prev_revenue * 100

        operating_margin = operating_income / revenue * 100
        net_margin = net_income / revenue * 100

        metrics.append(YearlyMetrics(
            year=row["year"],
            revenue=revenue,
            cogs=cogs,
            operating_expenses=op_expenses,
            net_income=net_income,
            operating_income=operating_income,
            revenue_growth=revenue_growth,
            operating_margin=operating_margin,
            net_margin=net_margin,
        ))

    return metrics


def build_context(metrics: list[YearlyMetrics]) -> str:
    """
    Build a formatted text table of all metrics to inject into the LLM prompt.
    Using plain ASCII so the model can easily parse and reference values.
    """
    header = (
        f"{'Year':>4}  {'Revenue':>10}  {'COGS':>10}  {'OpEx':>10}  "
        f"{'Op.Income':>10}  {'Net Income':>10}  "
        f"{'Rev.Growth':>11}  {'Op.Margin':>10}  {'Net Margin':>10}"
    )
    separator = "-" * len(header)

    lines = [header, separator]
    for m in metrics:
        growth_str = f"{m.revenue_growth:+.1f}%" if m.revenue_growth is not None else "    N/A  "
        lines.append(
            f"{m.year:>4}  {m.revenue:>10,}  {m.cogs:>10,}  {m.operating_expenses:>10,}  "
            f"{m.operating_income:>10,}  {m.net_income:>10,}  "
            f"{growth_str:>11}  {m.operating_margin:>9.1f}%  {m.net_margin:>9.1f}%"
        )

    lines += [
        separator,
        "",
        "Metric definitions:",
        "  Operating Income  = Revenue - COGS - Operating Expenses",
        "  Operating Margin  = Operating Income / Revenue * 100",
        "  Net Margin        = Net Income / Revenue * 100",
        "  Revenue Growth    = (Revenue_current - Revenue_prev) / Revenue_prev * 100",
    ]
    return "\n".join(lines)
