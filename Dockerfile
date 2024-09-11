FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install Flask gunicorn "psycopg[binary]"

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production


EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=1", "--threads=8", "--timeout=10"]