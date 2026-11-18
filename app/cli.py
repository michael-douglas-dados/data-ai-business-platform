"""Run a documented portfolio case against the synthetic local database."""
import argparse
import json
from . import analytics, pipeline, knowledge, sectors
from .seed import seed
from .store import connect

CSV_SAMPLE = "id,customer_id,day,amount,version\nDEMO-IMPORT,C001,2026-11-01,125.50,1\n"

def run_case(name):
    seed()
    actions = {
        "crm":analytics.customers,
        "etl":lambda:pipeline.ingest(CSV_SAMPLE),
        "quality":lambda: {"valid_rows":len(pipeline.validate_csv(CSV_SAMPLE)[0]),
                          "rejections":pipeline.validate_csv(CSV_SAMPLE.replace("125.50","NaN"))[1]},
        "warehouse":analytics.monthly,
        "reconciliation":pipeline.reconcile,
        "segmentation":analytics.customers,
        "retention":analytics.cohorts,
        "campaigns":analytics.campaign,
        "anomalies":analytics.anomalies,
        "documents":knowledge.chunks,
        "retrieval":lambda:knowledge.search("Qual regra de reativação considera frequência e recência?"),
        "evaluation":knowledge.evaluate,
        "investigation":lambda:knowledge.investigate("Como funciona a carga incremental?"),
        "procurement":sectors.procurement,
        "workforce":sectors.workforce,
        "forecast":sectors.forecast,
        "scoring":sectors.lead_scores,
        "exports":lambda:[{"customer_id":row["id"],"frequency":row["frequency"],
                          "monetary_cents":row["monetary_cents"]} for row in analytics.customers()]
    }
    if name == "incremental":
        # A separate ID lets this demonstration run repeatedly without changing existing fixtures.
        content = CSV_SAMPLE.replace("DEMO-IMPORT","DEMO-VERSION")
        first = pipeline.ingest(content)
        replay = pipeline.ingest(content)
        correction = pipeline.ingest(content.replace("125.50,1","130.00,2"))
        stale = pipeline.ingest(content)
        return {"first":first,"replay":replay,"correction":correction,"stale":stale}
    if name == "observability":
        with connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 10")]
    if name not in actions:
        raise ValueError("Projeto desconhecido")
    return actions[name]()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    args = parser.parse_args()
    print(json.dumps(run_case(args.project),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
