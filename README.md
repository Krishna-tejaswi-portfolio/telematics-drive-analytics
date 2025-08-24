# Drive Analytics — Local Demo (Ingest → Transform → Dashboards)

A **fully local** pipeline to demo:
- **FastAPI** ingestion → **Parquet (bronze)**
- **pandas** cleaning (silver) → **SQLite (gold)**
- **Apache Superset** dashboards

No cloud creds required. TODO placeholders show where to plug GCP/Azure later.

## Quickstart
```bash
make install           # create venv + install deps
make run-ingest        # start API at http://localhost:8080
make send-burst        # send 25 synthetic events
make process           # builds silver & gold datasets
make superset          # starts Superset on http://localhost:8088
