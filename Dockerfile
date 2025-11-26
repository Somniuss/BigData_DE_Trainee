FROM apache/airflow:2.7.1-python3.11

USER root
RUN apt-get update && apt-get install -y \
    vim \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
# Установка необходимых пакетов (если нужно)
# RUN pip install --no-cache-dir apache-airflow-providers-postgres
