FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY base_rag ./base_rag/

CMD ["sh", "-c", "uv run gunicorn -k uvicorn.workers.UvicornWorker -w $(nproc) -b 0.0.0.0:8005 --timeout 120 --proxy-headers base_rag.app.main:app"]