"""CSV ingestion, quality checks, versioned upserts and reconciliation."""
import csv
import io
import json
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from .store import connect

COLUMNS = ["id", "customer_id", "day", "amount", "version"]

def validate_csv(content):
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames != COLUMNS:
        raise ValueError("Colunas esperadas: " + ",".join(COLUMNS))
    valid, errors, seen = [], [], set()
    with connect() as connection:
        customers = {row["id"] for row in connection.execute("SELECT id FROM customers")}
    for number, row in enumerate(reader, 2):
        try:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("Número de colunas inválido")
            if not row["id"].strip() or row["id"] in seen:
                raise ValueError("ID vazio ou duplicado no arquivo")
            seen.add(row["id"])
            if row["customer_id"] not in customers:
                raise ValueError("Cliente inexistente")
            parsed = date.fromisoformat(row["day"])
            if parsed.isoformat() != row["day"]:
                raise ValueError("Data deve usar YYYY-MM-DD")
            amount = Decimal(row["amount"])
            if not amount.is_finite() or amount < 0:
                raise ValueError("Valor deve ser positivo ou zero, com até dois decimais")
            if amount > Decimal("100000000"):
                raise ValueError("Valor excede o limite da demonstração")
            if amount.as_tuple().exponent < -2:
                raise ValueError("Valor deve ter até dois decimais")
            version = int(row["version"])
            if not 1 <= version <= 2_147_483_647:
                raise ValueError("Versão deve estar entre 1 e 2147483647")
            valid.append((row["id"], row["customer_id"], row["day"], int(amount * 100), version))
        except (ValueError, InvalidOperation) as error:
            errors.append({"line": number, "reason": str(error)})
    return valid, errors

def ingest(content):
    started = time.perf_counter()
    rows, errors = validate_csv(content)
    changed = 0
    with connect() as connection:
        for row in rows:
            result = connection.execute("""
                INSERT INTO orders VALUES (?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET customer_id=excluded.customer_id,
                day=excluded.day, amount_cents=excluded.amount_cents, version=excluded.version
                WHERE excluded.version > orders.version
            """, row)
            changed += result.rowcount
        elapsed = round((time.perf_counter() - started) * 1000, 2)
        run = connection.execute(
            "INSERT INTO runs(input_rows,accepted,rejected,changed,elapsed_ms) VALUES (?,?,?,?,?)",
            (len(rows) + len(errors), len(rows), len(errors), changed, elapsed))
        connection.execute("INSERT INTO audits(action,detail) VALUES (?,?)",
                           ("ingestion", json.dumps({"run_id": run.lastrowid, "changed": changed})))
    return {"accepted": len(rows), "rejected": len(errors), "changed": changed, "errors": errors}

def reconcile():
    with connect() as connection:
        total = connection.execute("SELECT coalesce(sum(amount_cents),0) FROM orders").fetchone()[0]
        grouped = connection.execute("""
            SELECT customer_id, sum(amount_cents) total FROM orders GROUP BY customer_id
        """).fetchall()
        aggregate = sum(row["total"] for row in grouped)
        count = connection.execute("SELECT count(*) FROM orders").fetchone()[0]
    return {"source_cents": total, "aggregate_cents": aggregate, "difference_cents": total-aggregate,
            "orders": count, "balanced": total == aggregate}
