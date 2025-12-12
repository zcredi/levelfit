# Dockerfile for LEVEL FIT Telegram Bot
# 
# Использование:
# 1. Создайте .env файл с вашими токенами
# 2. Соберите образ: docker build -t levelfit-bot .
# 3. Запустите: docker run -d --name levelfit-bot --env-file .env levelfit-bot
#
# Или используйте docker-compose (см. docker-compose.yml)

FROM python:3.11-slim

# Установка метаданных
LABEL maintainer="LEVEL FIT"
LABEL description="Telegram bot for LEVEL FIT subscription payments"

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY bot.py .

# Создаем пользователя для безопасности (не root)
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Healthcheck (опционально)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# Запуск бота
CMD ["python3", "bot.py"]

