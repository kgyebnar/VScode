FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ANSIBLE_FORCE_COLOR=1

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-python.txt requirements.yml ./

RUN pip install --no-cache-dir -r requirements-python.txt && \
    ansible-galaxy collection install -r requirements.yml

COPY . .

RUN chmod +x tests/run_tests.sh

CMD ["./tests/run_tests.sh"]
