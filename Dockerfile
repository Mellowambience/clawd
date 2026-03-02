FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 18789

CMD ["uvicorn", "gateway.server:app", "--host", "0.0.0.0", "--port", "18789", "--log-level", "info"]
