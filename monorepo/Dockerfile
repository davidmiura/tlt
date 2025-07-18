# ────────────────
# STAGE 1: Build Next.js dashboard
# ────────────────
FROM node:20 AS nextjs_builder

WORKDIR /app/nextjs_app/dashboard

COPY nextjs_app/dashboard/package*.json ./
RUN npm install

COPY nextjs_app/dashboard ./
RUN npm run build

# ────────────────
# STAGE 2: Build Python with Poetry
# ────────────────
FROM python:3.12-slim AS python_builder

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .

# ────────────────
# STAGE 3: Final runtime container
# ────────────────
FROM caddy:2-alpine

# Install Python and runtime deps
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs \
    supervisor \
    curl \
    && ln -sf python3 /usr/bin/python

WORKDIR /app

# Copy Python environment
COPY --from=python_builder /app /app
COPY --from=python_builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python_builder /usr/local/bin /usr/local/bin

# Copy built Next.js app
COPY --from=nextjs_builder /app/nextjs_app/dashboard/.next /app/nextjs_app/dashboard/.next
COPY --from=nextjs_builder /app/nextjs_app/dashboard/public /app/nextjs_app/dashboard/public
COPY --from=nextjs_builder /app/nextjs_app/dashboard/node_modules /app/nextjs_app/dashboard/node_modules
COPY --from=nextjs_builder /app/nextjs_app/dashboard/package.json /app/nextjs_app/dashboard/package.json

# Copy Caddy configuration
COPY adapters/discord_adapter/Caddyfile /etc/caddy/Caddyfile

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directory for Caddy
RUN mkdir -p /var/log/caddy

EXPOSE 80 443 8001 8002 8003 8004 8008 3100

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
