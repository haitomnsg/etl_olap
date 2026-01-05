import requests
import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_URL = f"postgresql://{os.getenv('DW_USER')}:{os.getenv('DW_PASSWORD')}@dw_postgres:5432/{os.getenv('DW_DB')}"
engine = create_engine(DB_URL)

def run_etl():
    # 1. Extraction
    url = "https://api.open-meteo.com/v1/forecast?latitude=27.7&longitude=85.3&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Kathmandu"
    data = requests.get(url).json()
    daily = data["daily"]

    df = pd.DataFrame({
        "location": "Kathmandu",
        "weather_date": pd.to_datetime(daily["time"]),
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "precipitation": daily["precipitation_sum"],
    })

    # 2. Load to ODS
    with engine.begin() as conn:
        df.to_sql(
            "ods_weather",
            conn,
            if_exists="replace",
            index=False,
            method="multi"
        )
    # 3. Transformation to Star Schema
    with engine.begin() as conn:
        # Update Dimensions
        conn.execute(text("INSERT INTO dim_location (location) SELECT DISTINCT location FROM ods_weather ON CONFLICT DO NOTHING"))
        conn.execute(text("""
            INSERT INTO dim_date (date, year, month, day)
            SELECT DISTINCT weather_date, EXTRACT(YEAR FROM weather_date), EXTRACT(MONTH FROM weather_date), EXTRACT(DAY FROM weather_date)
            FROM ods_weather ON CONFLICT DO NOTHING
        """))

        # Clear Fact Table for fresh load
        conn.execute(text("TRUNCATE fact_weather"))

        # Transform Wide to Long and Insert into Fact
        # This SQL unpivots temp_max, temp_min, and precipitation into rows
        conn.execute(text("""
            INSERT INTO fact_weather (date_key, location_key, metric_key, value)
            SELECT d.date_key, l.location_key, m.metric_key, 
                   CASE m.metric_name 
                     WHEN 'temp_max' THEN o.temp_max 
                     WHEN 'temp_min' THEN o.temp_min 
                     WHEN 'precipitation' THEN o.precipitation 
                   END as value
            FROM ods_weather o
            JOIN dim_date d ON o.weather_date = d.date
            JOIN dim_location l ON o.location = l.location
            CROSS JOIN dim_metric m
        """))
    
    print("ETL: ODS -> Star Schema (Long Format) Complete")

if __name__ == "__main__":
    run_etl()