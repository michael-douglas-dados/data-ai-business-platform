"""Transactional storage for a local demonstration with synthetic customers."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, segment TEXT NOT NULL, consent INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS orders (
 id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id),
 day TEXT NOT NULL, amount_cents INTEGER NOT NULL CHECK(amount_cents >= 0),
 version INTEGER NOT NULL CHECK(version > 0));
CREATE TABLE IF NOT EXISTS deals (
 id INTEGER PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(id),
 title TEXT NOT NULL, value_cents INTEGER NOT NULL CHECK(value_cents >= 0),
 stage TEXT NOT NULL CHECK(stage IN ('novo','contato','proposta','ganho','perdido')),
 version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS events (
 event_id TEXT PRIMARY KEY, payload_hash TEXT NOT NULL, received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS audits (
 id INTEGER PRIMARY KEY, action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS campaigns (
 customer_id TEXT NOT NULL REFERENCES customers(id), campaign TEXT NOT NULL,
 state TEXT NOT NULL, PRIMARY KEY(customer_id,campaign));
CREATE TABLE IF NOT EXISTS runs (
 id INTEGER PRIMARY KEY, input_rows INTEGER NOT NULL, accepted INTEGER NOT NULL,
 rejected INTEGER NOT NULL, changed INTEGER NOT NULL, elapsed_ms REAL NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""

@contextmanager
def connect():
    path = Path(os.environ.get("WORKBENCH_DB", "runtime/workbench.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=20)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()

def initialize():
    with connect() as connection:
        connection.executescript(SCHEMA)
