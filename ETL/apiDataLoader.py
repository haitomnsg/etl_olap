import requests
import psycopg2
from datetime import datetime
import time

API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 27.70,
    "longitude": 85.32,
    "hourly": "temperature_2m,precipitation",
    "start": "2025-12-01T00:00:00Z",
    "end": "2025-12-02T00:00:00Z"
}

DB = {
    "dbname": "mydb",
    "user": "myuser",
    "password": "mypassword",
    "host": "postgres",
    "port": 5432
}

def get_connection(retries: int = 10, delay: int = 3):
    """Attempt to connect to Postgres with simple retry logic."""
    for attempt in range(1, retries + 1):
        try:
            return psycopg2.connect(**DB)
        except psycopg2.OperationalError as exc:
            if attempt == retries:
                raise
            print(f"Postgres not ready yet (attempt {attempt}/{retries}): {exc}")
            time.sleep(delay)

def main():
    data = requests.get(API_URL, params=PARAMS).json()

    conn = get_connection()
    cur = conn.cursor()

    # Location dimension
    cur.execute("""
        INSERT INTO dim_location (latitude, longitude)
        VALUES (%s, %s)
        ON CONFLICT (latitude, longitude)
        DO UPDATE SET latitude = EXCLUDED.latitude
        RETURNING location_id;
    """, (data["latitude"], data["longitude"]))
    location_id = cur.fetchone()[0]

    # Metric lookup: map metric_name -> metric_id
    cur.execute("SELECT metric_name, metric_id FROM dim_metric;")
    metrics = dict(cur.fetchall())

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    precs = data["hourly"]["precipitation"]

    for t, temp, prec in zip(times, temps, precs):
        dt = datetime.fromisoformat(t)
        date, hour = dt.date(), dt.hour

        # Time dimension
        cur.execute("""
            INSERT INTO dim_time (date, hour)
            VALUES (%s, %s)
            ON CONFLICT (date, hour)
            DO UPDATE SET date = EXCLUDED.date
            RETURNING time_id;
        """, (date, hour))
        time_id = cur.fetchone()[0]

        # Fact rows (3rd dimension!)
        cur.execute("""
            INSERT INTO fact_weather (time_id, location_id, metric_id, value)
            VALUES (%s, %s, %s, %s)
        """, (time_id, location_id, metrics['temperature'], temp))

        cur.execute("""
            INSERT INTO fact_weather (time_id, location_id, metric_id, value)
            VALUES (%s, %s, %s, %s)
        """, (time_id, location_id, metrics['precipitation'], prec))

    conn.commit()
    conn.close()
    print("✅ 3D OLAP cube loaded")

if __name__ == "__main__":
    main()
