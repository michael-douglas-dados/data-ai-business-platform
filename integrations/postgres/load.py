"""Copy synthetic local tables to a PostgreSQL analytics warehouse in one transaction."""
import os
import psycopg2
from psycopg2.extras import execute_values
from app.store import connect

def load():
    with connect() as source:
        customers = [tuple(row) for row in source.execute("SELECT id,name,segment,consent FROM customers")]
        orders = [tuple(row) for row in source.execute("SELECT id,customer_id,day,amount_cents,version FROM orders")]
    destination = psycopg2.connect(
        host=os.environ.get("PGHOST","127.0.0.1"),port=os.environ.get("PGPORT","55488"),
        dbname=os.environ.get("PGDATABASE","portfolio"),user=os.environ.get("PGUSER","portfolio"),
        password=os.environ["PGPASSWORD"],connect_timeout=10)
    try:
        with destination:
            with destination.cursor() as cursor:
                cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")
                cursor.execute("""CREATE TABLE IF NOT EXISTS raw.customers(
                    id text PRIMARY KEY,name text NOT NULL,segment text NOT NULL,consent boolean NOT NULL)""")
                cursor.execute("""CREATE TABLE IF NOT EXISTS raw.orders(
                    id text PRIMARY KEY,customer_id text REFERENCES raw.customers(id),
                    day date NOT NULL,amount_cents bigint NOT NULL CHECK(amount_cents>=0),version int NOT NULL)""")
                execute_values(cursor,"""INSERT INTO raw.customers VALUES %s ON CONFLICT(id) DO UPDATE
                    SET name=excluded.name,segment=excluded.segment,consent=excluded.consent""",
                    [(a,b,c,bool(d)) for a,b,c,d in customers])
                execute_values(cursor,"""INSERT INTO raw.orders VALUES %s ON CONFLICT(id) DO UPDATE
                    SET customer_id=excluded.customer_id,day=excluded.day,
                    amount_cents=excluded.amount_cents,version=excluded.version
                    WHERE excluded.version > raw.orders.version""",orders)
                cursor.execute("SELECT count(*),coalesce(sum(amount_cents),0) FROM raw.orders")
                count,total = cursor.fetchone()
        return {"warehouse":"postgresql","orders":count,"revenue_cents":total}
    finally:
        destination.close()

if __name__ == "__main__":
    print(load())
