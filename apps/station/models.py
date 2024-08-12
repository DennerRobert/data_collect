from django.db import models

class Station(models.Model):
    external_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255,null=True, blank=True)
    longitude = models.CharField(max_length=255,null=True, blank=True)
    access_link = models.CharField(max_length=255)
    county = models.CharField(max_length=255,null=True, blank=True)
    def __str__(self):
        return self.name


class Historical_data(models.Model):
    station = models.ForeignKey(Station, related_name='historical_data', on_delete=models.CASCADE)
    datetime = models.CharField(max_length=255,null=True, blank=True)
    battery = models.FloatField(null=True, blank=True)
    station_data = models.CharField(max_length=255,null=True, blank=True)

    def __str__(self):
        return f"{self.station.name} - {self.datetime}"
