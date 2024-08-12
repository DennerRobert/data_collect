from apps.station.models import Station, Historical_data
#referring to the serializers.py

def create_station_with_historical_data(validated_data):
    """
    Creates a station and its associated historical data.

    Args:
        validated_data (dict): A dictionary containing the validated data for the station and its historical data.

    Returns:
        Station: The created station instance.
    """
    historical_data = validated_data.pop('historical_data', [])
    station = Station.objects.create(**validated_data)
    for data in historical_data:
        Historical_data.objects.create(station=station, **data)
    return station


def update_station_with_historical_data(instance, validated_data):
    """
    Updates a station instance and its associated historical data.

    Args:
        instance (Station): The station instance to be updated.
        validated_data (dict): A dictionary containing the validated data for the station and its historical data.

    Returns:
        Station: The updated station instance.
    """
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