CREATE TABLE dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE,
    hour INT,
    UNIQUE (date, hour)
);

CREATE TABLE dim_location (
    location_id SERIAL PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    UNIQUE (latitude, longitude)
);

CREATE TABLE dim_metric (
    metric_id SERIAL PRIMARY KEY,
    metric_name TEXT UNIQUE
);

INSERT INTO dim_metric (metric_name)
VALUES ('temperature'), ('precipitation')
ON CONFLICT DO NOTHING;

CREATE TABLE fact_weather (
    fact_id SERIAL PRIMARY KEY,
    time_id INT REFERENCES dim_time(time_id),
    location_id INT REFERENCES dim_location(location_id),
    metric_id INT REFERENCES dim_metric(metric_id),
    value FLOAT
);
