# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy ETL code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir requests psycopg2-binary

# Default command: run the ETL script
CMD ["python", "apiDataLoader.py"]
