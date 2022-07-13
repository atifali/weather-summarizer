from django.shortcuts import render
from celery import Celery
import csv

app = Celery(
    'weather-summarizer',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='redis://redis',
)

# this is the hardcoded array that the app is expected to parse
# add more locations by filling out the 'test.csv' file
locations = []
# read the csv file with all the location information and put it in an array
with open('./summarizer/test.csv', 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        locations.append(row)

def index(request):
    # get all the location records here
    record_tasks = []
    for location in locations:
        record_tasks.append(
            app.send_task('fetchWeatherRecords', (float(location[1]), float(location[2])))
        )

    # parse them here to pass to the template
    location_records = []
    i = 0
    for record_task in record_tasks:
        weatherRecord = record_task.get()
        location_records.append(
            {
                'name' : locations[i][0],
                'day1metric' : weatherRecord[0],
                'day2metric' : weatherRecord[1],
                'day3metric' : weatherRecord[2],
                'day4metric' : weatherRecord[3],
                'day5metric' : weatherRecord[4],
            },
        )
        i = i + 1

    # get all the daily records
    daily_stats_task = app.send_task('processLocationRecords', ([location_records]))

    # parse the daily records here to pass to the template
    dailyStatsRecords = daily_stats_task.get()
    daily_records = []
    i = 0
    for dailyStatsRecord in dailyStatsRecords:
        daily_records.append(
            {
                'id' : i+1,
                'average' : dailyStatsRecord[0],
                'median' : dailyStatsRecord[1],
                'percentile25' : dailyStatsRecord[2],
                'percentile75' : dailyStatsRecord[3],
            },
        )
        i = i + 1


    context = {
        'location_records' : location_records,
        'daily_records' : daily_records,
        'days' : range(1,6)
    }
    return render(request, 'summarizer/index.html', context)
