#!/bin/bash
set -e

echo "Sprawdzanie/czyszczenie virtualenv..."
if [ ! -d "/app/.venv" ]; then
  echo "Tworzenie virtualenv..."
  uv venv /app/.venv
fi

# Zawsze aktywujemy (na wszelki wypadek)
source /app/.venv/bin/activate

# Upewniamy się, że zależności są zainstalowane (działa też z mountem)
echo "Instalacja/zaktualizowanie zależności..."
uv pip install -e ".[dev]" --no-cache-dir

echo "Inicjalizacja bazy danych..."
python -m flood_monitoring.scripts.init_db

echo "Uruchamianie API..."
exec uvicorn flood_monitoring.api.main:app --host 0.0.0.0 --port 8000 --reload