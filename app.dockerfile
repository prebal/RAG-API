FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim

WORKDIR /app

COPY --from=builder  /app/.venv ./.venv

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

COPY shell_scripts/app_entrypoint.sh /app_entrypoint.sh

RUN chmod +x /app_entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app_entrypoint.sh"]

