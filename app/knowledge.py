"""Local lexical retrieval with source attribution and explicit evaluation."""
import re
import time
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1] / "data" / "knowledge"

def chunks():
    result = []
    for file in sorted(ROOT.glob("*.md")):
        for index, paragraph in enumerate(file.read_text(encoding="utf-8").split("\n\n")):
            if paragraph.strip():
                result.append({"id": f"{file.stem}-{index}", "source": file.name, "text":paragraph.strip()})
    return result

def search(question, limit=3):
    started = time.perf_counter()
    documents = chunks()
    if not documents:
        return {"matches":[],"elapsed_ms":0}
    vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1,2))
    matrix = vectorizer.fit_transform([doc["text"] for doc in documents])
    scores = cosine_similarity(vectorizer.transform([question]),matrix)[0]
    ranked = sorted(zip(documents,scores), key=lambda item: (-item[1],item[0]["id"]))
    matches = [{**doc,"score":round(float(score),4)} for doc,score in ranked[:limit] if score >= 0.08]
    return {"matches":matches, "elapsed_ms":round((time.perf_counter()-started)*1000,2),
            "method":"TF-IDF lexical retrieval"}

def evaluate():
    cases = [
        ("Qual regra de reativação considera frequência e recência?", "reactivation.md"),
        ("Como funciona a versão da carga incremental?", "pipeline.md"),
        ("Qual o critério de consentimento das campanhas?", "consent.md"),
        ("Como analisar um alerta de anomalia?", "anomalies.md"),
    ]
    results = []
    for question, source in cases:
        found = search(question)
        ranks = [index+1 for index,item in enumerate(found["matches"]) if item["source"] == source]
        rank = ranks[0] if ranks else None
        results.append({"question":question,"expected":source,"rank":rank,
                        "reciprocal_rank":1/rank if rank else 0,"elapsed_ms":found["elapsed_ms"]})
    return {"cases":results,"recall_at_3":sum(row["rank"] is not None for row in results)/len(results),
            "mrr":sum(row["reciprocal_rank"] for row in results)/len(results),
            "scope":"Fixture pequena e sintética; mede recuperação lexical, não qualidade de geração."}

def investigate(topic):
    from .analytics import overview
    from .pipeline import reconcile
    # Tools are selected from a fixed allowlist. Input is never executed as SQL or Python.
    trace = [{"tool":"reconcile","result":reconcile()},
             {"tool":"overview","result":overview()},
             {"tool":"knowledge_search","result":search(topic)}]
    return {"mode":"deterministic_tool_workflow","steps":trace,
            "conclusion":"Conciliação consistente" if trace[0]["result"]["balanced"] else "Revisar conciliação"}
