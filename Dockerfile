FROM python:3.9-slim

RUN apt-get update && apt-get install -y tzdata
ENV TZ=Asia/Taipei
RUN dpkg-reconfigure -f noninteractive tzdata

ENV PYTHONBUFFERED=True
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install "psycopg[binary]"

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers=1", "--timeout=10", "--log-level=debug", "--access-logfile=-", "--error-logfile=-"]
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app --log-level debug --access-logfile - --error-logfile -