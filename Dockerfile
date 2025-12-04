from python:3.12-slim

workdir /app

run apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

copy requirements.txt .


run pip install --no-cache-dir -r requirements.txt

copy . .


expose 8000


cmd ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]