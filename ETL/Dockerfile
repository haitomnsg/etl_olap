FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 if needed (slim versions often need these)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ETL script
COPY main.py .

# Run the script
CMD ["python", "main.py"]