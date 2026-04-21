FROM python:3.11-slim

# Evita la creazione di file .pyc (mantiene il container pulito)
ENV PYTHONDONTWRITEBYTECODE=1
# Assicura che i log vengano stampati subito nel terminale di Docker
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installa le dipendenze di sistema necessarie per PostgreSQL e compilazione
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e installa i requisiti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice
COPY . .

CMD ["python", "main.py"]