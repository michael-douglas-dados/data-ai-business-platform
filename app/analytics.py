"""Business rules are explicit and use a reproducible as-of date."""
from collections import defaultdict
from datetime import date
from .store import connect

AS_OF = date(2026, 11, 17)

def customers():
    with connect() as connection:
        records = connection.execute("""
            SELECT c.*, count(o.id) frequency, coalesce(sum(o.amount_cents),0) monetary_cents,
            max(o.day) last_purchase FROM customers c LEFT JOIN orders o ON c.id=o.customer_id
            AND o.day <= ? GROUP BY c.id ORDER BY monetary_cents DESC, c.id
        """, (AS_OF.isoformat(),)).fetchall()
    result = []
    for record in records:
        item = dict(record)
        item["recency_days"] = (AS_OF-date.fromisoformat(item["last_purchase"])).days if item["last_purchase"] else None
        item["audience"] = audience(item["recency_days"], item["frequency"], item["consent"])
        result.append(item)
    return result

def audience(recency, frequency, consent):
    if not consent:
        return "Sem consentimento"
    if recency is None:
        return "Sem compras"
    if recency >= 60 and frequency >= 2:
        return "Reativação"
    if recency <= 30 and frequency >= 3:
        return "Recorrente"
    return "Acompanhamento"

def monthly():
    with connect() as connection:
        return [dict(row) for row in connection.execute("""
            SELECT substr(day,1,7) month, sum(amount_cents) revenue_cents, count(*) orders
            FROM orders WHERE day <= ? GROUP BY substr(day,1,7) ORDER BY month
        """, (AS_OF.isoformat(),))]

def cohorts():
    with connect() as connection:
        orders = connection.execute("SELECT customer_id,day FROM orders WHERE day<=? ORDER BY day",
                                    (AS_OF.isoformat(),)).fetchall()
    first, members, activity = {}, defaultdict(set), defaultdict(set)
    for order in orders:
        customer = order["customer_id"]
        month = order["day"][:7]
        first.setdefault(customer, month)
        cohort = first[customer]
        members[cohort].add(customer)
        year, month_number = map(int, month.split("-"))
        first_year, first_month = map(int, cohort.split("-"))
        age = (year-first_year)*12+month_number-first_month
        activity[(cohort, age)].add(customer)
    results = []
    for cohort in sorted(members):
        year, month_number = map(int, cohort.split("-"))
        observed_age = (AS_OF.year-year)*12 + AS_OF.month-month_number
        for age in range(observed_age+1):
            results.append({"cohort": cohort, "month_index": age, "size": len(members[cohort]),
                            "active": len(activity[(cohort,age)]),
                            "retention": round(len(activity[(cohort,age)])/len(members[cohort]),4)})
    return results

def anomalies():
    from sklearn.ensemble import IsolationForest
    with connect() as connection:
        orders = [dict(row) for row in connection.execute("SELECT id,amount_cents FROM orders ORDER BY id")]
    if len(orders) < 10:
        return {"method": "IsolationForest", "items": [], "status": "insufficient_data"}
    model = IsolationForest(contamination=0.03, random_state=42, n_estimators=100)
    predictions = model.fit_predict([[row["amount_cents"]] for row in orders])
    scores = model.decision_function([[row["amount_cents"]] for row in orders])
    items = [{**row, "score": round(float(score),4)} for row, prediction, score in zip(orders,predictions,scores)
             if prediction == -1]
    return {"method": "IsolationForest", "items": items, "status": "review_required"}

def campaign():
    selected = [item for item in customers() if item["audience"] == "Reativação"]
    added = 0
    with connect() as connection:
        # Recompute the current audience in the transaction before inserting.
        connection.execute("""
            DELETE FROM campaigns WHERE state='pending_review' AND customer_id NOT IN (
                SELECT c.id FROM customers c JOIN orders o ON c.id=o.customer_id
                WHERE c.consent=1 AND o.day<=? GROUP BY c.id
                HAVING count(*)>=2 AND julianday(?)-julianday(max(o.day))>=60
            )
        """, (AS_OF.isoformat(), AS_OF.isoformat()))
        for item in selected:
            eligible = connection.execute("""
                SELECT c.id FROM customers c JOIN orders o ON c.id=o.customer_id
                WHERE c.id=? AND c.consent=1 AND o.day<=? GROUP BY c.id
                HAVING count(*)>=2 AND julianday(?)-julianday(max(o.day))>=60
            """, (item["id"],AS_OF.isoformat(),AS_OF.isoformat())).fetchone()
            if eligible:
                added += connection.execute(
                    "INSERT OR IGNORE INTO campaigns VALUES (?,?,?)",
                    (item["id"], "reactivation-2026-11", "pending_review")).rowcount
    return {"eligible":len(selected),"added":added,"delivery":"pending_review"}

def overview():
    people = customers()
    return {"customers":len(people),"revenue_cents":sum(p["monetary_cents"] for p in people),
            "reactivation":sum(p["audience"]=="Reativação" for p in people),
            "as_of":AS_OF.isoformat(),"monthly":monthly()}
