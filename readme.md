# Weather Data Warehouse

A containerized data warehouse project that extracts hourly weather data from the Open-Meteo API and loads it into a PostgreSQL star schema for OLAP analysis.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Open-Meteo    │      │    PostgreSQL   │      │    Superset     │
│      API        │─────▶│   Data Warehouse│◀─────│   Dashboards    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        ▲
        │                        │
        └────────────────────────┘
                  ETL Script
```

## Services

| Service    | Port  | Description                          |
|------------|-------|--------------------------------------|
| PostgreSQL | 5432  | Data warehouse (star schema)         |
| Superset   | 8088  | BI dashboards and visualization      |
| Mondrian   | 8080  | OLAP server for MDX queries          |
| Python ETL | -     | Extracts and loads weather data      |

## Star Schema

### Dimension Tables
- **dim_time** – Date and hour
- **dim_location** – Latitude and longitude
- **dim_metric** – Metric type (temperature, precipitation)

### Fact Table
- **fact_weather** – Weather measurements linked to time, location, and metric dimensions

## Quick Start

### 1. Start all services

```bash
docker compose up -d
```

### 2. Run the ETL script

```bash
docker compose up python
```

This fetches weather data from Open-Meteo API and loads it into the data warehouse.

### 3. Access Superset

Open [http://localhost:8088](http://localhost:8088)

- **Username:** `admin`
- **Password:** `admin`

### 4. Connect Superset to PostgreSQL

1. Go to **Settings → Database Connections**
2. Click **+ Database** → **PostgreSQL**
3. Use this SQLAlchemy URI:
   ```
   postgresql://myuser:mypassword@postgres:5432/mydb
   ```
4. Test connection and save

### 5. Create a Dataset

1. Go to **Data → Datasets → + Dataset**
2. Select database: your Postgres connection
3. Select schema: `public`
4. Select table: `fact_weather`
5. Save and start exploring!

## Useful Commands

### Check loaded data

```bash
# Count fact rows
docker compose exec postgres psql -U myuser -d mydb -c "SELECT COUNT(*) FROM fact_weather;"

# View sample data
docker compose exec postgres psql -U myuser -d mydb -c "SELECT * FROM fact_weather LIMIT 10;"

# View dimensions
docker compose exec postgres psql -U myuser -d mydb -c "SELECT * FROM dim_time LIMIT 10;"
docker compose exec postgres psql -U myuser -d mydb -c "SELECT * FROM dim_location;"
docker compose exec postgres psql -U myuser -d mydb -c "SELECT * FROM dim_metric;"
```

### View service logs

```bash
docker compose logs -f superset
docker compose logs -f postgres
docker compose logs python
```

### Restart services

```bash
docker compose down
docker compose up -d
```

### Reset database (wipe all data)

```bash
docker compose down -v
docker compose up -d
```

## Configuration

### ETL Parameters

Edit `ETL/apiDataLoader.py` to change:

- **Location:** `latitude`, `longitude` in `PARAMS`
- **Date range:** `start`, `end` in `PARAMS`
- **Metrics:** `hourly` parameter (e.g., `temperature_2m,precipitation`)

### Database Credentials

All services use these credentials (defined in `docker-compose.yml`):

| Setting  | Value      |
|----------|------------|
| Database | `mydb`     |
| User     | `myuser`   |
| Password | `mypassword` |

## Project Structure

```
DataWareHouse/
├── docker-compose.yml    # Container orchestration
├── readme.md             # This file
└── ETL/
    ├── apiDataLoader.py  # ETL script (extract, transform, load)
    ├── schema.sql        # Star schema DDL
    ├── Dockerfile        # Python container build
    └── requirements.txt  # Python dependencies
```

## API Reference

This project uses the [Open-Meteo API](https://open-meteo.com/) for weather data.

Example API call:
```
https://api.open-meteo.com/v1/forecast?latitude=27.70&longitude=85.32&hourly=temperature_2m,precipitation
```