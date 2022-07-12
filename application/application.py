import time
import random

from celery import Celery

# Wait for rabbitmq to be started
time.sleep(20)

print('Application started')

app = Celery(
    'weather-summarizer',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='redis://redis',
)

numTasks = 100
tasks = []

for i in range(numTasks):
    time.sleep(2.0 * random.random())  # Random delay
    tasks.append(
        app.send_task('addTask', (i, 3))  # Send task by name
    )
    print('Sent task:', i)

for task in tasks:
    result = task.get()
    print('Received result:', result)

print('Application ended')
