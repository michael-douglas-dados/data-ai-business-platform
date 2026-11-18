"""Airflow 3 DAG; install the repository package path on the Airflow worker."""
from datetime import datetime, timezone
from airflow.sdk import dag, task

@dag(schedule="@daily",start_date=datetime(2026,11,1,tzinfo=timezone.utc),catchup=False,
     tags=["portfolio","synthetic"],max_active_runs=1)
def business_pipeline():
    @task(retries=2)
    def ingest_fixture():
        from app.seed import seed
        return seed()

    @task
    def reconcile_after_load(_load):
        from app.pipeline import reconcile
        result = reconcile()
        if not result["balanced"]:
            raise ValueError("Revenue reconciliation failed")
        return result

    @task
    def evaluate_retrieval(_reconciliation):
        from app.knowledge import evaluate
        result = evaluate()
        if result["recall_at_3"] < 0.75:
            raise ValueError("Retrieval regression")
        return result

    evaluate_retrieval(reconcile_after_load(ingest_fixture()))

business_pipeline()
