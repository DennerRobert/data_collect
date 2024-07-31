import requests
from bs4 import BeautifulSoup
from .models import Station
from datetime import datetime
from .models import Historical_data
from django.utils.dateparse import parse_datetime


def scrape_station_data():
    url = 'http://sinda.crn.inpe.br/PCD/SITE/novo/site/cidades.php?uf=RN'
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all('tr')
    stations = []

    for row in rows[2:]:  # Pulando a primeira linha que é o cabeçalho
        cells = row.find_all('td')
        if len(cells) >= 3:
            external_id = cells[0].get_text(strip=True)
            station_name = cells[1].get_text(strip=True)
            county = cells[2].get_text(strip=True)
            link = cells[0].find('a')['onclick'].split("'")[1]

            detail_url = f'http://sinda.crn.inpe.br/PCD/SITE/novo/site/{link}'
            stations.append({
                'external_id': external_id,
                'name': station_name,
                'access_link': detail_url,
                'county': county
            })
    
    return stations


def save_station_data(stations):
    stations = scrape_station_data()

    station_updates = []
    historical_data = []

    for station_info in stations:
        station, created = Station.objects.update_or_create(
            external_id=station_info['external_id'],
            defaults={'name': station_info['name'], 'access_link': station_info['access_link']}
        )

        detail_response = requests.get(station_info['access_link'])
        detail_response.encoding = 'utf-8'
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

        rows2 = detail_soup.find_all('tr')
        if rows2:
            row2 = rows2[1]
            cells2 = row2.find_all('td')

            if len(cells2) >= 6:
                latitude = cells2[4].get_text(strip=True)
                longitude = cells2[5].get_text(strip=True)

                station.latitude = latitude if latitude else None
                station.longitude = longitude if longitude else None
                station_updates.append(station)

            if len(rows2) > 3:
                for row2 in rows2[3:]:
                    cells3 = row2.find_all('td')
                    if len(cells3) >= 3:
                        datetime_str = cells3[0].get_text(strip=True)
                        battery = cells3[1].get_text(strip=True)
                        station_data = cells3[2].get_text(strip=True)
                        battery = 0 if battery == '' else battery
                        station_data = 0 if not station_data and not battery else station_data

                        try:
                            datetime_obj = parse_datetime(datetime_str)
                        except ValueError:
                            print(f'Error converting datetime: {datetime_str}')
                            continue

                        if not Historical_data.objects.filter(
                                station=station,
                                datetime=datetime_obj
                            ).exists():
                            historical_data.append(
                                Historical_data(
                                    station=station,
                                    datetime=datetime_obj,
                                    battery=battery,
                                    station_data=station_data
                                )
                            )

    if station_updates:
        Station.objects.bulk_update(station_updates, ['latitude', 'longitude'])

    if historical_data:
        Historical_data.objects.bulk_create(historical_data)
    else:
        print('No historical data to save.')