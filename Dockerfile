FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system dependencies (important for Django + cryptography + Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . /app/

# collect static (safe even if empty)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["gunicorn", "moussa_company.wsgi:application", "--bind", "0.0.0.0:8000"]