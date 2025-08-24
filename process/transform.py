import glob
from pathlib import Path
import pandas as pd

BRONZE = Path("warehouse/bronze")
SILVER = Path("warehouse/silver")
SILVER.mkdir(parents=True, exist_ok=True)

def load_bronze() -> pd.DataFrame:
    files = sorted(glob.glob(str(BRONZE / "raw_events_*.parquet")))
    if not files:
        print("No bronze files found. Send events first (make send-burst).")
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    # Required fields
    df = df.dropna(subset=["device_id","trip_id","ts","lat","lon"])
    # Valid lat/lon
    df = df[(df["lat"].between(-90,90)) & (df["lon"].between(-180,180))]
    # Clamp unrealistic speeds
    if "speed" in df.columns:
        df.loc[(df["speed"] < 0) | (df["speed"] > 200), "speed"] = None
    # Deduplicate by key keeping latest ingest_ts
    df["key"] = df["device_id"] + "|" + df["trip_id"] + "|" + df["ts"].astype(str)
    df = df.sort_values(["key","ingest_ts"]).drop_duplicates("key", keep="last")
    df = df.drop(columns=["key"])
    return df

def main():
    df = load_bronze()
    df = clean(df)
    out = SILVER / "events_clean.parquet"
    df.to_parquet(out, index=False)
    print(f"silver written: {out} rows={len(df)}")

if __name__ == "__main__":
    main()
