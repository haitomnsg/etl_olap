-- ODS TABLE
CREATE TABLE IF NOT EXISTS ods_weather (
    id SERIAL PRIMARY KEY,
    location TEXT,
    weather_date DATE,
    temp_max FLOAT,
    temp_min FLOAT,
    precipitation FLOAT
);

-- DIMENSIONS
CREATE TABLE IF NOT EXISTS dim_date (
    date_key SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    year INT,
    month INT,
    day INT
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    location TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_metric (
    metric_key SERIAL PRIMARY KEY,
    metric_name TEXT UNIQUE
);

-- FACT TABLE
CREATE TABLE IF NOT EXISTS fact_weather (
    date_key INT REFERENCES dim_date(date_key),
    location_key INT REFERENCES dim_location(location_key),
    metric_key INT REFERENCES dim_metric(metric_key),
    value FLOAT
);

-- Pre-seed the metrics
INSERT INTO dim_metric (metric_name) VALUES ('temp_max'), ('temp_min'), ('precipitation')
ON CONFLICT DO NOTHING;