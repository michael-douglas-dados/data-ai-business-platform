"""Local demo API. Bind to loopback; production requires authentication and authorization."""
import csv
import io
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .store import connect, initialize
from . import analytics, pipeline, knowledge, sectors

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Customer(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,32}$")
    name: str = Field(min_length=2,max_length=100)
    segment: Literal["Serviços","Comércio","Tecnologia"]
    consent: bool

class Deal(StrictModel):
    customer_id: str = Field(min_length=1,max_length=32)
    title: str = Field(min_length=2,max_length=100)
    value_cents: int = Field(ge=0,le=10_000_000_000)

class Stage(StrictModel):
    stage: Literal["novo","contato","proposta","ganho","perdido"]
    version: int = Field(ge=1)

class CSVInput(StrictModel):
    content: str = Field(min_length=1,max_length=1_000_000)

class Question(StrictModel):
    question: str = Field(min_length=3,max_length=500)

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app = FastAPI(title="Customer Data Workbench",version="1.0.0",lifespan=lifespan)

@app.middleware("http")
async def local_origin(request: Request, call_next):
    # Browsers from arbitrary origins cannot mutate the local demonstration.
    origin = request.headers.get("origin")
    if request.method not in ("GET","HEAD","OPTIONS") and origin and origin not in {
        "http://127.0.0.1:5188","http://localhost:5188",
        "http://127.0.0.1:8088","http://localhost:8088"
    }:
        return Response("Origem não permitida",status_code=403)
    return await call_next(request)

@app.get("/api/health")
def health():
    return {"status":"ok","dataset":"synthetic","mode":"local_demo"}

@app.get("/api/overview")
def overview():
    return analytics.overview()

@app.get("/api/customers")
def customers():
    return analytics.customers()

@app.post("/api/customers",status_code=201)
def create_customer(customer: Customer):
    with connect() as connection:
        result = connection.execute("INSERT INTO customers VALUES (?,?,?,?) ON CONFLICT(id) DO NOTHING",
                                    (customer.id,customer.name,customer.segment,int(customer.consent)))
        if result.rowcount != 1:
            raise HTTPException(409,"ID de cliente já existe")
        connection.execute("INSERT INTO audits(action,detail) VALUES (?,?)",("customer_created",customer.id))
    return customer

@app.get("/api/deals")
def deals():
    with connect() as connection:
        return [dict(row) for row in connection.execute("""
            SELECT d.*, c.name customer FROM deals d JOIN customers c ON c.id=d.customer_id ORDER BY d.id
        """)]

@app.post("/api/deals",status_code=201)
def create_deal(deal: Deal):
    with connect() as connection:
        if not connection.execute("SELECT 1 FROM customers WHERE id=?",(deal.customer_id,)).fetchone():
            raise HTTPException(404,"Cliente não encontrado")
        cursor = connection.execute("INSERT INTO deals(customer_id,title,value_cents,stage) VALUES (?,?,?,'novo')",
                                    (deal.customer_id,deal.title,deal.value_cents))
        connection.execute("INSERT INTO audits(action,detail) VALUES (?,?)",("deal_created",str(cursor.lastrowid)))
        return {"id":cursor.lastrowid,"stage":"novo","version":1}

@app.patch("/api/deals/{deal_id}")
def move_deal(deal_id: int, change: Stage):
    with connect() as connection:
        current = connection.execute("SELECT * FROM deals WHERE id=?",(deal_id,)).fetchone()
        if current is None:
            raise HTTPException(404,"Oportunidade não encontrada")
        result = connection.execute("UPDATE deals SET stage=?,version=version+1 WHERE id=? AND version=?",
                                    (change.stage,deal_id,change.version))
        if result.rowcount != 1:
            raise HTTPException(409,"Oportunidade alterada. Atualize a página e tente novamente.")
        connection.execute("INSERT INTO audits(action,detail) VALUES (?,?)",
                           ("deal_stage",json.dumps({"id":deal_id,"from":current["stage"],"to":change.stage})))
    return {"id":deal_id,"stage":change.stage,"version":change.version+1}

@app.post("/api/pipeline/validate")
def validate(payload: CSVInput):
    try:
        rows, errors = pipeline.validate_csv(payload.content)
        return {"accepted":len(rows),"rejected":len(errors),"errors":errors}
    except ValueError as error:
        raise HTTPException(422,str(error)) from error

@app.post("/api/pipeline/run")
def run(payload: CSVInput):
    try:
        return pipeline.ingest(payload.content)
    except ValueError as error:
        raise HTTPException(422,str(error)) from error

@app.get("/api/reconcile")
def reconciliation():
    return pipeline.reconcile()

@app.get("/api/cohorts")
def cohorts():
    return analytics.cohorts()

@app.get("/api/anomalies")
def anomalies():
    return analytics.anomalies()

@app.post("/api/campaigns/prepare")
def campaign():
    return analytics.campaign()

@app.get("/api/campaigns")
def campaigns():
    with connect() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM campaigns ORDER BY customer_id")]

@app.get("/api/operations")
def operations():
    with connect() as connection:
        return {"runs":[dict(row) for row in connection.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 30")],
                "audit":[dict(row) for row in connection.execute("SELECT * FROM audits ORDER BY id DESC LIMIT 50")]}

@app.get("/api/knowledge")
def documents():
    return knowledge.chunks()

@app.post("/api/search")
def search(question: Question):
    return knowledge.search(question.question)

@app.post("/api/investigate")
def investigate(question: Question):
    return knowledge.investigate(question.question)

@app.get("/api/evaluations")
def evaluations():
    return knowledge.evaluate()

@app.get("/api/procurement")
def procurement():
    return sectors.procurement()

@app.get("/api/workforce")
def workforce():
    return sectors.workforce()

@app.get("/api/forecast")
def forecast():
    return sectors.forecast()

@app.get("/api/lead-scores")
def lead_scores():
    return sectors.lead_scores()

@app.get("/api/export/customers")
def export_customers():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["customer_id","segment","frequency","recency_days","monetary_cents","audience"])
    for row in analytics.customers():
        writer.writerow([row["id"],row["segment"],row["frequency"],row["recency_days"],
                         row["monetary_cents"],row["audience"]])
    return Response(output.getvalue(),media_type="text/csv",
                    headers={"Content-Disposition":"attachment; filename=customer_metrics.csv"})

@app.get("/api/projects")
def projects():
    path = Path(__file__).resolve().parents[1]/"data"/"projects.json"
    return json.loads(path.read_text(encoding="utf-8"))

build = Path(__file__).resolve().parents[1]/"web"/"dist"
if build.exists():
    app.mount("/",StaticFiles(directory=build,html=True),name="web")
