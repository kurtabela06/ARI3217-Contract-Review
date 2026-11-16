FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src ./src
COPY config ./config

RUN pip install --no-cache-dir --no-deps .

RUN contract-train \
    && rm -rf /app/data /root/.cache/kagglehub

EXPOSE 8888

CMD ["uvicorn", "contract_review.api:app", "--host", "0.0.0.0", "--port", "8888"]
