import pandas as pd
from pathlib import Path
from math import acos, cos, sin, radians

SILVER_FILE = Path("warehouse/silver/events_clean.parquet")
GOLD_DIR = Path("warehouse/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_PATH = GOLD_DIR / "gold.db"

def hav_km(lat1, lon1, lat2, lon2):
    # simple great-circle distance in km
    return 111.111 * acos(
        max(-1.0, min(1.0,
            cos(radians(lat1))*cos(radians(lat2))*cos(radians(lon1 - lon2)) +
            sin(radians(lat1))*sin(radians(lat2))
        ))
    )

def calc_trip_kpis(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    df = df.sort_values(["device_id","trip_id","ts"])
    df["prev_lat"] = df.groupby(["device_id","trip_id"])["lat"].shift(1)
    df["prev_lon"] = df.groupby(["device_id","trip_id"])["lon"].shift(1)
    mask = df["prev_lat"].notna()

    df["segment_km"] = 0.0
    df.loc[mask, "segment_km"] = df[mask].apply(
        lambda r: hav_km(r["lat"], r["lon"], r["prev_lat"], r["prev_lon"]), axis=1
    )

    trips = df.groupby(["device_id","trip_id"], as_index=False).agg(
        trip_start=("ts","min"),
        trip_end=("ts","max"),
        distance_km=("segment_km","sum"),
        avg_speed=("speed","mean"),
        max_speed=("speed","max")
    )
    return trips

def calc_fleet_daily(trips: pd.DataFrame) -> pd.DataFrame:
    if trips.empty: return trips
    trips["day"] = pd.to_datetime(trips["trip_start"]).dt.date
    daily = trips.groupby("day", as_index=False).agg(
        trips=("trip_id","count"),
        total_km=("distance_km","sum"),
        avg_of_avg_speed=("avg_speed","mean"),
        fleet_max_speed=("max_speed","max")
    ).sort_values("day")
    daily["trips_change_pct"] = daily["trips"].pct_change().fillna(0)*100
    daily["km_change_pct"]    = daily["total_km"].pct_change().fillna(0)*100
    return daily

def main():
    if not SILVER_FILE.exists():
        print("silver not found. Run: make transform"); return
    df = pd.read_parquet(SILVER_FILE)
    trips = calc_trip_kpis(df)
    daily = calc_fleet_daily(trips)

    import sqlite3
    conn = sqlite3.connect(SQLITE_PATH)
    trips.to_sql("trip_kpis", conn, if_exists="replace", index=False)
    daily.to_sql("fleet_daily_kpis", conn, if_exists="replace", index=False)
    conn.close()
    print(f"gold SQLite written: {SQLITE_PATH}")
    print(f"tables: trip_kpis({len(trips)}), fleet_daily_kpis({len(daily)})")

if __name__ == "__main__":
    main()
