from django.db import models

class Day(models.Model):
    date = models.DateField('date')


class Metrics(models.Model):
    temp = models.IntegerField(default=0)


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()


class LocationMetrics(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    metrics = models.OneToOneField(Metrics, on_delete=models.CASCADE)


class MetricStats(models.Model):
    average = models.FloatField()
    median = models.FloatField()
    percentile25 = models.FloatField()
    percentile75 = models.FloatField()


class DailyStats(models.Model):
    day = models.OneToOneField(Day, on_delete=models.CASCADE)
    temp = models.OneToOneField(MetricStats, on_delete=models.CASCADE)

