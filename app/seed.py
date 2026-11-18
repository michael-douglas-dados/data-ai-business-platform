"""Reproducible synthetic fixtures, never copied from a business database."""
import csv
import io
import random
from datetime import date, timedelta
from .store import initialize, connect
from .pipeline import ingest

def seed():
    initialize()
    rng = random.Random(42)
    with connect() as connection:
        for number in range(1,41):
            connection.execute("INSERT OR IGNORE INTO customers VALUES (?,?,?,?)",
                               (f"C{number:03}",f"Cliente demonstração {number:02}",
                                ["Serviços","Comércio","Tecnologia"][number%3],int(number%7!=0)))
        if connection.execute("SELECT count(*) FROM orders").fetchone()[0]:
            return {"status":"already_seeded"}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","customer_id","day","amount","version"])
    for number in range(1,241):
        customer = number % 40 + 1
        offset = rng.randrange(0,210) if customer%4 else rng.randrange(90,210)
        day = date(2026,11,17)-timedelta(days=offset)
        amount = 990000 if number==239 else rng.randrange(10000,130000)
        writer.writerow([f"O{number:04}",f"C{customer:03}",day.isoformat(),f"{amount/100:.2f}",1])
    report = ingest(output.getvalue())
    with connect() as connection:
        if not connection.execute("SELECT count(*) FROM deals").fetchone()[0]:
            for index in range(1,9):
                connection.execute("INSERT INTO deals(customer_id,title,value_cents,stage) VALUES (?,?,?,?)",
                                   (f"C{index:03}",f"Renovação de contrato {index}",index*25000,
                                    ["novo","contato","proposta","ganho"][index%4]))
    return report

if __name__ == "__main__":
    print(seed())
