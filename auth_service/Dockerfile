FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

RUN chmod +x entrypoint.sh

ENV PYTHONPATH=/app

CMD ["./entrypoint.sh"]
