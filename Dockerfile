FROM python:3.11-slim AS builder

WORKDIR /build

COPY prodRequirements.txt .

RUN pip install --no-cache-dir -r prodRequirements.txt


FROM python:3.11-slim AS app

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY ./src ./app

# create non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

CMD ["python", "./app/main.py"]
