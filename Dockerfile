FROM python:3.11-slim

ENV PLAYWRIGHT_BROWSERS_PATH=/home/playwright/.cache/ms-playwright
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install

COPY .env .
COPY config.py .
COPY app.py .

RUN echo "0 19 * * * /usr/local/bin/python /usr/src/app/app.py >> /var/log/cron.log 2>&1" > /etc/crontab

RUN chmod 0644 /etc/crontab

CMD ["cron", "-f"]