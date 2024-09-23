FROM python:3.12-slim

RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Taipei
RUN dpkg-reconfigure -f noninteractive tzdata

ENV PYTHONBUFFERED=True
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install Flask gunicorn "psycopg[binary]"

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=1", "--threads=8", "--timeout=10", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]