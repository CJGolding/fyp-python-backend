FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY tests/requirements.txt ./tests/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r tests/requirements.txt

COPY . .

RUN coverage run --omit '.venv/*' -m pytest -v tests/ && coverage report -m

EXPOSE 8000

CMD ["uvicorn", "fastapi_entrypoint:app", "--host", "0.0.0.0", "--port", "8000"]

