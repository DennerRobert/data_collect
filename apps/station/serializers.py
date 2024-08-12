from rest_framework import serializers
from .models import Station, Historical_data
from rest_framework import viewsets
from rest_framework.response import Response


class HistoricalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historical_data
        fields = ['id', 'datetime', 'battery', 'station_data', 'station']

class StationSerializer(serializers.ModelSerializer):
    historical_data = HistoricalDataSerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = ['id', 'external_id', 'name', 'historical_data', 'latitude', 'longitude']

class StationCreateSerializer(serializers.ModelSerializer):
    historical_data = HistoricalDataSerializer(many=True, required=False)

    class Meta:
        model = Station
        fields = ['id', 'external_id', 'name', 'latitude', 'longitude', 'historical_data']

    def create(self, validated_data):
        historical_data = validated_data.pop('historical_data', [])
        station = Station.objects.create(**validated_data)
        for data in historical_data:
            Historical_data.objects.create(station=station, **data)
        return station
    
    def update(self, instance, validated_data):
        instance.external_id = validated_data.get('external_id', instance.external_id)
        instance.name = validated_data.get('name', instance.name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)

        historical_data = validated_data.get('historical_data', [])
        for data in historical_data:
            historical_entry = Historical_data.objects.get(id=data.get('id'))
            historical_entry.datetime = data.get('datetime', historical_entry.datetime)
            historical_entry.battery = data.get('battery', historical_entry.battery)
            historical_entry.station_data = data.get('station_data', historical_entry.station_data)
            historical_entry.save()

        instance.save()
        return instance

    
class HistoricalDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historical_data
        fields = ['datetime', 'battery', 'station_data']