import time
import random

from celery import Celery

# Wait for rabbitmq to be started
time.sleep(10)

app = Celery(
    'weather-summarizer',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='redis://redis',
)

@app.task(name='addTask')  # Named task
def add(x, y):
    print('Task Add started')
    time.sleep(10.0 * random.random())  # Simulate a long task
    print('Task Add done')
    return x + y
