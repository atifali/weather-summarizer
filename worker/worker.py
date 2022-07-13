import time
import statistics
import math

import requests
from celery import Celery

# Wait for rabbitmq to be started
time.sleep(10)

app = Celery(
    'weather-summarizer',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='redis://redis',
)

# this is just a dummy API key
#  get yours here: https://openweathermap.org/
API_KEY = 'saldnlkasdl3e23e23nklenlk2ndio2dnoi2dn20d23'

def getDailyAverage(records):
    sum = 0 
    for record in records:
        sum = sum + record['main']['temp']
    return sum/len(records)

def getPercentile(data, perc: int):
    size = len(data)
    return sorted(data)[int(math.ceil((size * perc) / 100)) - 1]

@app.task(name='fetchWeatherRecords')  # Named task
def fetchWeatherRecords(lat, long):
    print('Fetching weather records now for: ', lat, long)
    getURL = 'https://api.openweathermap.org/data/2.5/forecast?lat=%.15f&lon=%.15f&appid=%s' % (lat, long, API_KEY)
    r = requests.get(getURL)
    records = r.json()['list']
    nextDay = (int(time.time() / 86400) + 1) * 86400
    
    sanitizedRecords = []
    for record in records:
        if record['dt'] >= nextDay:
            sanitizedRecords.append(record)
    
    weatherRecord = []
    # this is super bad, quick and dirty!
    # same here - needs refactoring!
    day1Records = sanitizedRecords[0:8]
    weatherRecord.append(getDailyAverage(day1Records))
    day2Records = sanitizedRecords[8:16]
    weatherRecord.append(getDailyAverage(day2Records))
    day3Records = sanitizedRecords[16:24]
    weatherRecord.append(getDailyAverage(day3Records))
    day4Records = sanitizedRecords[24:32]
    weatherRecord.append(getDailyAverage(day4Records))
    remainingRecords = len(sanitizedRecords)%8
    day5Records = sanitizedRecords[-1*remainingRecords:]
    weatherRecord.append(getDailyAverage(day5Records))
    
    print('Done fetching weather records for: ', lat, long)
    return weatherRecord


@app.task(name='processLocationRecords')  # Named task
def processLocationRecords(locationRecords=[]):
    dailyStatsTasks = []
    for day in range(5):
        dailyRecords = []
        metricID = 'day%dmetric' % (day+1)
        for locationRecord in locationRecords:
            dailyRecords.append(locationRecord[metricID])
        dailyStatsTasks.append(
            app.send_task('processDailyStats', ([dailyRecords]))
        )
    
    dailyStatsRecords = []
    for dailyStatsTask in dailyStatsTasks:
        while not dailyStatsTask.ready():
            time.sleep(0.01)
        dailyStatsRecord = dailyStatsTask.result
        dailyStatsRecords.append(dailyStatsRecord)
    
    return dailyStatsRecords


@app.task(name='processDailyStats')  # Named task
def processDailyStats(dailyRecords=[]):
    dailyStats = []
    # average
    dailyStats.append(
        statistics.mean(dailyRecords)
    )
    # median
    dailyStats.append(
        statistics.median(dailyRecords)
    )
    # percentile25
    dailyStats.append(
        getPercentile(dailyRecords, 25)
    )
    # percentile75
    dailyStats.append(
        getPercentile(dailyRecords, 75)
    )

    return dailyStats

