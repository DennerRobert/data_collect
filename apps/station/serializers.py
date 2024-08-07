from rest_framework import serializers
from .models import Station, Historical_data
from rest_framework import viewsets
from rest_framework.response import Response


class HistoricalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historical_data
        fields = ['datetime', 'battery', 'station_data']

class StationSerializer(serializers.ModelSerializer):
    historical_data = HistoricalDataSerializer(many=True, read_only=True)

    class Meta:
        model = Station
        fields = ['id', 'external_id', 'name', 'historical_data', 'latitude', 'longitude']

class StationCreateSerializer(serializers.ModelSerializer):
    historical_data = HistoricalDataSerializer(many=True, required=False)

    class Meta:
        model = Station
        fields = ['id', 'external_id', 'name', 'historical_data', 'latitude', 'longitude']

    def create(self, validated_data):
        historical_data = validated_data.pop('historical_data', [])
        station = Station.objects.create(**validated_data)
        for historical_data_ in historical_data:
            Historical_data.objects.create(station=station, **historical_data_)
        return station
    
    def list(self, request, station_pk=None):
        historical_data = Historical_data.objects.filter(station_id=station_pk)
        serializer = HistoricalDataSerializer(historical_data, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, station_pk=None):
        station = Station.objects.get(id=station_pk)
        serializer_station = StationSerializer(station)
        historical_data = Historical_data.objects.filter(station=station)
        historical_data_serializer = HistoricalDataSerializer(historical_data, many=True)
        return Response({
            'station': serializer_station.data,
            'historical_data': historical_data_serializer.data
        })
    
class HistoricalDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historical_data
        fields = ['datetime', 'battery', 'station_data']