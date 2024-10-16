FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости, необходимые для psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY poetry.lock pyproject.toml ./

# Устанавливаем Poetry
RUN python -m pip install --no-cache-dir poetry==1.8.3

# Устанавливаем зависимости без dev-пакетов
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Копируем все файлы проекта
COPY . .

# Копируем скрипт entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh  # Убедитесь, что скрипт исполняемый

RUN pip cache purge && poetry cache clear --all pypi
RUN apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
