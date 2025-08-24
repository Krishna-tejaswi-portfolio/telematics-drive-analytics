from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

# Local "warehouse" paths
BRONZE_DIR = Path("warehouse/bronze")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

def append_event_to_parquet(event: dict):
    """
    Append event to a daily parquet file in bronze.
    """
    row = dict(event)
    row["ingest_ts"] = datetime.now(timezone.utc).isoformat()
    day = str(row["ts"])[:10]  # YYYY-MM-DD
    p = BRONZE_DIR / f"raw_events_{day}.parquet"

    df = pd.DataFrame([row])
    if p.exists():
        old = pd.read_parquet(p)
        df = pd.concat([old, df], ignore_index=True)
    df.to_parquet(p, index=False)

# === TODO (cloud) ===
# Replace parquet write with Pub/Sub publish, or direct write to GCS.
# Read GCP project/region/bucket from environment variables set by Secret Manager/Key Vault.
# Never commit real secrets; use OIDC in CI/CD and runtime secret mounts.
