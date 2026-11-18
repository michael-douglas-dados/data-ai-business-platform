"""Regression tests for the public synthetic demonstration."""
import csv
import io
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.api import app
from app import analytics, knowledge, pipeline, sectors
from app.seed import seed
from app.store import connect

HEADER = "id,customer_id,day,amount,version\n"


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"WORKBENCH_DB": str(Path(self.directory.name)/"test.db")})
        self.environment.start()
        self.client = TestClient(app)
        self.client.__enter__()
        seed()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.environment.stop()
        self.directory.cleanup()

    def clear_orders(self):
        with connect() as connection:
            connection.execute("DELETE FROM orders")
            connection.execute("DELETE FROM runs")
            connection.execute("DELETE FROM audits")

    def test_seed_is_repeatable_without_duplicate_orders(self):
        before = pipeline.reconcile()
        seed()
        self.assertEqual(pipeline.reconcile(), before)
        self.assertEqual(before["orders"], 240)

    def test_validation_rejects_invalid_values_with_line_numbers(self):
        content = HEADER + "\n".join([
            "bad1,C001,2026-11-01,NaN,1",
            "bad2,C001,2026-11-01,Infinity,1",
            "bad3,C001,2026-11-01,1.001,1",
            "bad4,C001,2026-11-01,-1,1",
            "bad5,C999,2026-11-01,10,1",
            "bad6,C001,2026-02-30,10,1",
            "bad7,C001,20261101,10,1",
            "bad8,C001,2026-11-01,10,0",
            "bad9,C001,2026-11-01,10,no",
            "bad10,C001,2026-11-01,100000001,1",
        ])
        rows, errors = pipeline.validate_csv(content)
        self.assertEqual(rows, [])
        self.assertEqual([error["line"] for error in errors], list(range(2,12)))

    def test_malformed_schema_returns_422_without_writes(self):
        before = pipeline.reconcile()
        response = self.client.post("/api/pipeline/run",json={"content":"id,value\n1,99"})
        self.assertEqual(response.status_code,422)
        self.assertEqual(pipeline.reconcile(),before)

    def test_extreme_numeric_inputs_are_quarantined_without_server_error(self):
        self.clear_orders()
        content = HEADER + "A,C001,2026-11-01,10,2147483648\nB,C001,2026-11-01,1e999999999,1\nC,C001,2026-11-01,10,2147483647\nD,C001,2026-11-01,1e-999999999,1\n"
        response = self.client.post("/api/pipeline/run",json={"content":content})
        self.assertEqual(response.status_code,200)
        self.assertEqual((response.json()["accepted"],response.json()["rejected"]),(1,3))
        self.assertEqual(pipeline.reconcile()["source_cents"],1000)

    def test_partial_batch_quarantines_invalid_rows_and_rejects_duplicate_id(self):
        self.clear_orders()
        report = pipeline.ingest(HEADER+"X,C001,2026-11-01,10.01,1\nX,C001,2026-11-01,90,2\nY,C999,2026-11-01,1,1\nZ,C001,2026-11-01,0,1\n")
        self.assertEqual((report["accepted"], report["rejected"],report["changed"]),(2,2,2))
        self.assertEqual(pipeline.reconcile()["source_cents"],1001)

    def test_import_uses_exact_cents(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"X,C001,2026-11-01,0.10,1\nY,C001,2026-11-01,0.20,1\n")
        self.assertEqual(pipeline.reconcile()["source_cents"],30)

    def test_retry_and_stale_version_cannot_overwrite_correction(self):
        self.clear_orders()
        original = HEADER+"X,C001,2026-11-01,10,1\n"
        self.assertEqual(pipeline.ingest(original)["changed"],1)
        self.assertEqual(pipeline.ingest(original)["changed"],0)
        self.assertEqual(pipeline.ingest(HEADER+"X,C002,2026-11-02,20,2\n")["changed"],1)
        self.assertEqual(pipeline.ingest(original)["changed"],0)
        with connect() as connection:
            record = dict(connection.execute("SELECT * FROM orders WHERE id='X'").fetchone())
        self.assertEqual((record["amount_cents"],record["version"],record["customer_id"]),(2000,2,"C002"))

    def test_failed_transaction_rolls_back_all_rows_and_audit(self):
        self.clear_orders()
        with connect() as connection:
            connection.execute("""CREATE TRIGGER stop_bad BEFORE INSERT ON orders
                WHEN NEW.id='STOP' BEGIN SELECT RAISE(ABORT,'forced transaction failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            pipeline.ingest(HEADER+"OK,C001,2026-11-01,10,1\nSTOP,C001,2026-11-01,20,1\n")
        with connect() as connection:
            for table in ("orders","runs","audits"):
                self.assertEqual(connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0],0)

    def test_reconciliation_matches_overview_and_monthly_with_known_fixture(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"A,C001,2026-10-01,10,1\nB,C002,2026-11-01,20,1\n")
        self.assertEqual(pipeline.reconcile()["source_cents"],3000)
        overview = analytics.overview()
        self.assertEqual(overview["revenue_cents"],3000)
        self.assertEqual(sum(row["revenue_cents"] for row in overview["monthly"]),3000)

    def test_future_orders_are_excluded_from_as_of_metrics(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"A,C001,2026-11-17,10,1\nB,C001,2026-12-01,90,1\n")
        customer = next(row for row in analytics.customers() if row["id"]=="C001")
        self.assertEqual((customer["frequency"],customer["monetary_cents"],customer["recency_days"]),(1,1000,0))

    def test_campaign_boundary_consent_and_idempotence(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"\n".join([
            "A,C001,2026-09-01,10,1","B,C001,2026-09-18,10,1",
            "C,C002,2026-09-01,10,1","D,C002,2026-09-19,10,1",
            "E,C007,2026-09-01,10,1","F,C007,2026-09-18,10,1",
            "G,C003,2026-09-01,10,1",
        ]))
        first = analytics.campaign()
        self.assertEqual((first["eligible"],first["added"]),(1,1))
        self.assertEqual(analytics.campaign()["added"],0)
        rows = self.client.get("/api/campaigns").json()
        self.assertEqual([(row["customer_id"],row["state"]) for row in rows],[("C001","pending_review")])

    def test_cohort_uses_unique_customers_and_zero_months(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"\n".join([
            "A,C001,2026-08-01,10,1","B,C001,2026-08-02,10,1",
            "C,C002,2026-08-03,10,1","D,C001,2026-10-01,10,1",
        ]))
        rows = [row for row in analytics.cohorts() if row["cohort"]=="2026-08"]
        self.assertEqual([row["active"] for row in rows],[2,0,1,0])
        self.assertEqual([row["retention"] for row in rows],[1,0,0.5,0])
        self.assertTrue(all(row["size"]==2 for row in rows))

    def test_campaign_removes_pending_customer_after_consent_revocation(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"A,C001,2026-09-01,10,1\nB,C001,2026-09-18,10,1\n")
        self.assertEqual(analytics.campaign()["added"],1)
        with connect() as connection:
            connection.execute("UPDATE customers SET consent=0 WHERE id='C001'")
        self.assertEqual(analytics.campaign()["eligible"],0)
        self.assertEqual(self.client.get("/api/campaigns").json(),[])

    def test_campaign_removes_pending_customer_after_recent_purchase(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"A,C001,2026-09-01,10,1\nB,C001,2026-09-18,10,1\n")
        analytics.campaign()
        pipeline.ingest(HEADER+"C,C001,2026-11-17,10,1\n")
        analytics.campaign()
        self.assertEqual(self.client.get("/api/campaigns").json(),[])

    def test_customer_create_duplicate_and_unknown_field(self):
        customer = {"id":"NEW","name":"Cliente de teste","segment":"Tecnologia","consent":False}
        self.assertEqual(self.client.post("/api/customers",json=customer).status_code,201)
        self.assertEqual(self.client.post("/api/customers",json=customer).status_code,409)
        self.assertEqual(self.client.post("/api/customers",json={**customer,"admin":True}).status_code,422)

    def test_deal_optimistic_lock_prevents_stale_update(self):
        response = self.client.post("/api/deals",json={"customer_id":"C001","title":"Novo contrato","value_cents":12345})
        self.assertEqual(response.status_code,201)
        deal_id = response.json()["id"]
        changed = self.client.patch(f"/api/deals/{deal_id}",json={"stage":"proposta","version":1})
        self.assertEqual(changed.status_code,200)
        self.assertEqual(changed.json()["version"],2)
        stale = self.client.patch(f"/api/deals/{deal_id}",json={"stage":"ganho","version":1})
        self.assertEqual(stale.status_code,409)
        current = next(row for row in self.client.get("/api/deals").json() if row["id"]==deal_id)
        self.assertEqual(current["stage"],"proposta")
        audit = self.client.get("/api/operations").json()["audit"]
        self.assertEqual(sum(row["action"]=="deal_stage" for row in audit),1)

    def test_deal_rejects_invalid_amount_customer_stage(self):
        self.assertEqual(self.client.post("/api/deals",json={"customer_id":"absent","title":"Contrato","value_cents":100}).status_code,404)
        self.assertEqual(self.client.post("/api/deals",json={"customer_id":"C001","title":"Contrato","value_cents":-100}).status_code,422)
        self.assertEqual(self.client.patch("/api/deals/1",json={"stage":"arbitrary","version":1}).status_code,422)
        self.assertEqual(self.client.patch("/api/deals/99999",json={"stage":"ganho","version":1}).status_code,404)

    def test_untrusted_browser_origin_cannot_mutate(self):
        response = self.client.post("/api/campaigns/prepare",headers={"Origin":"https://untrusted.example"})
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.client.get("/api/campaigns").json(),[])

    def test_export_has_exact_row_count_and_no_names(self):
        response = self.client.get("/api/export/customers")
        self.assertEqual(response.status_code,200)
        records = list(csv.DictReader(io.StringIO(response.text)))
        self.assertEqual(len(records),40)
        self.assertNotIn("name",records[0])
        self.assertEqual(sum(int(row["monetary_cents"]) for row in records),analytics.overview()["revenue_cents"])

    def test_no_match_query_returns_empty_sources(self):
        self.assertEqual(knowledge.search("zxqwv abcxyz 918273645")["matches"],[])

    def test_retrieval_has_real_source_and_reproducible_ranking(self):
        query = "versão da carga incremental"
        first = knowledge.search(query)["matches"]
        second = knowledge.search(query)["matches"]
        self.assertEqual(first,second)
        self.assertTrue(first)
        self.assertEqual(first[0]["source"],"pipeline.md")
        known = {item["id"]:item for item in knowledge.chunks()}
        for item in first:
            self.assertEqual(item["text"],known[item["id"]]["text"])

    def test_evaluation_matches_declared_fixture(self):
        result = knowledge.evaluate()
        self.assertEqual(len(result["cases"]),4)
        self.assertEqual(result["recall_at_3"],1.0)
        self.assertGreaterEqual(result["mrr"],0.5)

    def test_investigation_does_not_execute_arbitrary_sql(self):
        result = knowledge.investigate("DROP TABLE customers;")
        self.assertEqual(result["mode"],"deterministic_tool_workflow")
        self.assertEqual([step["tool"] for step in result["steps"]],["reconcile","overview","knowledge_search"])
        self.assertEqual(len(analytics.customers()),40)

    def test_anomalies_reproducible_and_include_extreme_value(self):
        first = analytics.anomalies()
        self.assertEqual(first,analytics.anomalies())
        self.assertEqual(first["status"],"review_required")
        self.assertIn("O0239",[item["id"] for item in first["items"]])

    def test_insufficient_data_does_not_fit_model(self):
        self.clear_orders()
        self.assertEqual(analytics.anomalies()["status"],"insufficient_data")
        self.assertEqual(sectors.forecast()["status"],"insufficient_history")

    def test_forecast_holdout_excludes_partial_month(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"\n".join([
            "A,C001,2026-07-01,100,1","B,C001,2026-08-01,200,1",
            "C,C001,2026-09-01,300,1","D,C001,2026-10-01,400,1",
            "E,C001,2026-11-01,999999,1",
        ]))
        forecast = sectors.forecast()
        self.assertEqual(forecast["next_month_cents"],30000)
        self.assertEqual(forecast["backtest_mae_cents"],20000)
        self.assertEqual(forecast["backtest_points"],1)

    def test_procurement_shares_and_delivery_denominators(self):
        rows = sectors.procurement()
        self.assertAlmostEqual(sum(row["share"] for row in rows),1)
        supplier = next(row for row in rows if row["supplier"]=="Fornecedor-demo-A")
        self.assertEqual((supplier["spend_cents"],supplier["orders"],supplier["on_time_rate"]),(260000,2,0.5))

    def test_forecast_fills_internal_and_trailing_missing_months(self):
        self.clear_orders()
        pipeline.ingest(HEADER+"A,C001,2026-07-01,300,1\nB,C001,2026-09-01,600,1\n")
        forecast = sectors.forecast()
        # Completed months are July 300, August 0, September 600, October 0.
        self.assertEqual(forecast["next_month_cents"],20000)
        self.assertEqual(forecast["backtest_mae_cents"],30000)
        self.assertEqual(forecast["backtest_points"],1)

    def test_workforce_rate_is_weighted_by_scheduled_hours(self):
        rows = sectors.workforce()
        operations = next(row for row in rows if row["department"]=="Operações")
        self.assertEqual(operations["scheduled_hours"],320)
        self.assertEqual(operations["absence_rate"],8/320)
        self.assertEqual(operations["cost_cents"],930000)

    def test_lead_score_blocks_nonconsenting_customers(self):
        scores = sectors.lead_scores()
        blocked = next(row for row in scores if row["id"]=="C007")
        self.assertEqual(blocked["score"],0)
        self.assertTrue(blocked["reasons"])
        self.assertEqual([row["score"] for row in scores],sorted([row["score"] for row in scores],reverse=True))


if __name__ == "__main__":
    unittest.main()
