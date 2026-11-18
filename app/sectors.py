"""Additional industry cases with fully synthetic inputs and explicit denominators."""
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

DATA = Path(__file__).resolve().parents[1] / "data"

def procurement():
    grouped = defaultdict(lambda: {"spend_cents":0,"orders":0,"late":0})
    with (DATA/"purchases.csv").open(encoding="utf-8",newline="") as file:
        for row in csv.DictReader(file):
            item = grouped[row["supplier"]]
            item["spend_cents"] += int(row["amount_cents"])
            item["orders"] += 1
            item["late"] += int(row["delay_days"]) > 0
    total = sum(item["spend_cents"] for item in grouped.values())
    return [{"supplier":name,**item,"share":item["spend_cents"]/total if total else 0,
             "on_time_rate":1-item["late"]/item["orders"]} for name,item in sorted(grouped.items())]

def workforce():
    grouped = defaultdict(lambda: {"scheduled_hours":0,"absent_hours":0,"cost_cents":0,"people":0})
    with (DATA/"workforce.csv").open(encoding="utf-8",newline="") as file:
        for row in csv.DictReader(file):
            item = grouped[row["department"]]
            for field in ("scheduled_hours","absent_hours","cost_cents"):
                item[field] += int(row[field])
            item["people"] += 1
    return [{"department":name,**item,
             "absence_rate":item["absent_hours"]/item["scheduled_hours"] if item["scheduled_hours"] else 0}
            for name,item in sorted(grouped.items())]

def forecast():
    from .analytics import monthly, AS_OF
    history = [row for row in monthly() if row["month"] < AS_OF.strftime("%Y-%m")]
    values = []
    if history:
        by_month = {row["month"]:row["revenue_cents"] for row in history}
        year, month = map(int, history[0]["month"].split("-"))
        while (year, month) < (AS_OF.year, AS_OF.month):
            values.append(by_month.get(f"{year:04}-{month:02}", 0))
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    if len(values) < 4:
        return {"status":"insufficient_history"}
    predictions = [mean(values[i-3:i]) for i in range(3,len(values))]
    errors = [abs(actual-predicted) for actual,predicted in zip(values[3:],predictions)]
    return {"method":"Média móvel de três meses completos","next_month_cents":round(mean(values[-3:])),
            "backtest_mae_cents":round(mean(errors)), "backtest_points":len(errors),
            "status":"baseline_synthetic_data"}

def lead_scores():
    from .analytics import customers
    result = []
    for customer in customers():
        recency = customer["recency_days"]
        reasons = []
        score = 0
        if customer["consent"]:
            if recency is not None and recency <= 90:
                score += 40
                reasons.append("Compra nos últimos 90 dias")
            if customer["frequency"] >= 3:
                score += 30
                reasons.append("Pelo menos três compras")
            if customer["monetary_cents"] >= 300000:
                score += 30
                reasons.append("Receita acumulada a partir de R$ 3.000")
        else:
            reasons.append("Contato bloqueado por ausência de consentimento")
        result.append({"id":customer["id"],"name":customer["name"],"score":score,"reasons":reasons})
    return sorted(result,key=lambda row:(-row["score"],row["id"]))
