FROM python:3

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT celery -A worker worker --autoscale 100 --loglevel=info
