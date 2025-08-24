.PHONY: venv install run-ingest send-one send-burst transform kpis process superset up all clean

venv:
	python -m venv .venv

install: venv
	. .venv/bin/activate && pip install -r ingest_app/requirements.txt
	. .venv/bin/activate && pip install -r process/requirements.txt

run-ingest:
	. .venv/bin/activate && uvicorn ingest_app.main:app --host 0.0.0.0 --port 8080

send-one:
	curl -X POST "http://localhost:8080/ingest/event" \
	  -H "Content-Type: application/json" \
	  -d @data/samples/sample_event.json

send-burst:
	python - <<'PY'
import requests, json, random, datetime
url="http://localhost:8080/ingest/event"
base=json.load(open("data/samples/sample_event.json"))
for i in range(25):
    e=base.copy()
    e["ts"]=(datetime.datetime.utcnow()+datetime.timedelta(seconds=i)).isoformat()+"Z"
    e["speed"]=max(0, min(140, (e.get("speed") or 50)+random.randint(-20,20)))
    e["rpm"]=max(600, min(4500, (e.get("rpm") or 2000)+random.randint(-300,300)))
    requests.post(url, json=e, timeout=5)
print("sent 25 events")
PY

transform:
	. .venv/bin/activate && python process/transform.py

kpis:
	. .venv/bin/activate && python process/kpis.py

process: transform kpis

superset:
	cd serving/superset && docker compose up -d

up: install run-ingest

all: install run-ingest

clean:
	rm -rf .venv warehouse
