from fastapi import FastAPI, HTTPException
from .models import TelemetryEvent
from .storage import append_event_to_parquet

app = FastAPI(title="Ingestion API (Local Demo)")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/ingest/event")
def ingest(evt: TelemetryEvent):
    try:
        append_event_to_parquet(evt.model_dump())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
