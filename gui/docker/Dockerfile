FROM node:18-alpine AS frontend-build
WORKDIR /build/frontend

COPY gui/frontend/package*.json ./
RUN npm install

COPY gui/frontend/ ./
RUN npm run build

FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    DB_PATH=/data/gui.db \
    PLAYBOOK_DIR=/app \
    BACKUP_DIR=/data/backups \
    LOG_DIR=/data/logs \
    BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000 \
    FRONTEND_PORT=80 \
    NGINX_PORT=80 \
    ANSIBLE_CONFIG=/app/ansible.cfg \
    DEBUG=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ansible \
    nginx \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY gui/backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

COPY requirements.yml ./requirements.yml
RUN ansible-galaxy collection install -r ./requirements.yml

COPY gui/backend ./backend
COPY gui/docker/nginx.om2248.conf /etc/nginx/conf.d/default.conf
COPY gui/docker/entrypoint.sh ./entrypoint.sh
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
COPY ansible.cfg ./ansible.cfg
COPY inventory ./inventory
COPY group_vars ./group_vars
COPY vars ./vars
COPY templates ./templates
COPY palo_alto_firewall_upgrade.yml ./palo_alto_firewall_upgrade.yml
COPY palo_alto_firewall_rollback.yml ./palo_alto_firewall_rollback.yml

RUN mkdir -p /data/backups /data/logs /run/nginx \
    && rm -f /etc/nginx/sites-enabled/default \
    && chmod +x /app/entrypoint.sh

EXPOSE 80 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read()"

CMD ["/app/entrypoint.sh"]
