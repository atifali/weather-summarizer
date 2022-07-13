FROM python:3

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT python -u manage.py runserver 0.0.0.0:8000
