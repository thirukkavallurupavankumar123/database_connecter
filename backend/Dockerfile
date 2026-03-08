FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client libs for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8000

# Runs migrations then starts uvicorn
CMD ["bash", "start.sh"]
