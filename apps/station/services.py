from apps.station.models import Station, Historical_data


def create_station_with_historical_data(validated_data):
    """Cria uma estação e seus dados históricos associados."""
    historical_data = validated_data.pop('historical_data', [])
    station = Station.objects.create(**validated_data)
    for data in historical_data:
        Historical_data.objects.create(station=station, **data)
    return station


def update_station_with_historical_data(instance, validated_data):
    """Atualiza uma estação e seus dados históricos associados."""
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