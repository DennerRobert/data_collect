from rest_framework import serializers
from apps.station.services import create_station_with_historical_data, update_station_with_historical_data
from .models import Station, Historical_data


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
        """
        Creates a new station instance and its associated historical data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the station and its historical data.

        Returns:
            Station: The newly created station instance.
        """
        return create_station_with_historical_data(validated_data)
    
    def update(self, instance, validated_data):
        """
        Updates an existing station instance and its associated historical data.

        Args:
            instance (Station): The station instance to be updated.
            validated_data (dict): A dictionary containing the validated data for the station and its historical data.

        Returns:
            Station: The updated station instance.
        """
        return update_station_with_historical_data(instance, validated_data)

    
class HistoricalDataCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historical_data
        fields = ['datetime', 'battery', 'station_data']