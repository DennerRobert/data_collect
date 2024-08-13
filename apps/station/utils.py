import requests
from bs4 import BeautifulSoup
from .models import Station, Historical_data
from django.utils.dateparse import parse_datetime
from .serializers import HistoricalDataCreateSerializer, StationCreateSerializer
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense


def scrape_station_data():
    """
    Scrapes station data from a given website.

    This function sends a GET request to the specified URL, parses the HTML response,
    and extracts relevant information about weather stations. It returns a list of
    dictionaries, each containing the external ID, name, access link, and county of a station.

    Returns:
        list: A list of dictionaries containing station data.
    """
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
    """
    Saves station data by scraping the provided website, updating or creating station objects,
    and saving their historical data.

    Args:
        stations (list): A list of station data dictionaries.
    """
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


def create_historical_data_for_station(station, data):
    """
    Creates historical data for a given station based on the provided data.

    Args:
        station: The station for which historical data is being created.
        data: A list of dictionaries containing historical data to be created.
    """
    for item in data:
        Historical_data.objects.create(station=station, **item)


def handle_create_historical_data(request, station_pk):
    """
    Handles the creation of historical data for a specific station.

    Args:
        request: The incoming request containing historical data to be created.
        station_pk: The primary key of the station for which historical data is being created.

    Returns:
        Response: A successful response with the created historical data if the request is valid, otherwise a response with error details.
    """
    station = Station.objects.get(id=station_pk)
    serializer = HistoricalDataCreateSerializer(data=request.data, many=True)
    
    if serializer.is_valid():
        create_historical_data_for_station(station, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def handle_station_update(request, pk, partial):
    """
    Handles the update of a station, either with a `PUT` or `PATCH` request.

    Args:
        request: The incoming request containing the updated station data.
        pk: The primary key of the station to be updated.
        partial: A boolean indicating whether the update is partial or not.

    Returns:
        Response: A successful response with the updated station data if the request is valid,
                  otherwise a response with error details.
    """
    try:
        station = Station.objects.get(pk=pk)
    except Station.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StationCreateSerializer(station, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def analyze_station_data(data, prediction_steps=4):
    """
    Analyzes the given station data and makes predictions using a LSTM model.

    Args:
        data (pandas.DataFrame): The station data to be analyzed, containing columns 'datetime' and 'battery'.
        prediction_steps (int, optional): The number of steps to predict ahead. Defaults to 4.

    Returns:
        dict: A dictionary containing the predictions made by the LSTM model. The key 'station_data_predictions'
              maps to a list of floats representing the predicted battery levels.

    Description:
        This function takes in a pandas DataFrame containing station data with columns 'datetime' and 'battery'.
        It converts the 'datetime' column to an index, ensures that the 'battery' column is numeric, and drops any
        rows with missing values. It then normalizes the data using the MinMaxScaler.

        The function prepares the data for the LSTM model by creating input and output sequences. It reshapes the
        input data to have the shape (num_sequences, sequence_length, 1) and reshapes the output data to have the
        shape (num_sequences, 1).

        The function defines and trains an LSTM model with two LSTM layers and a Dense layer. It compiles the model with
        the Adam optimizer and mean squared error loss. It fits the model to the input and output data using 20 epochs
        and a batch size of 32.

        The function then makes predictions by iteratively feeding the last sequence of the scaled data into the model
        and appending the predicted values to the 'predictions' list. It descales the predictions before returning
        them as a dictionary with the key 'station_data_predictions'.
    """
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)

    data['battery'] = pd.to_numeric(data['battery'], errors='coerce')
    data = data.dropna()

    # Normalizar os dados entre 0 e 1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['battery']])

    # Preparar dados para LSTM
    X, y = [], []
    for i in range(len(scaled_data) - prediction_steps):
        X.append(scaled_data[i:i+prediction_steps, 0])
        y.append(scaled_data[i+prediction_steps, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Definir e treinar o modelo LSTM
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=20, batch_size=32)

    # Fazer previsões
    predictions = []
    last_sequence = scaled_data[-prediction_steps:]
    current_input = last_sequence

    for i in range(prediction_steps):
        prediction = model.predict(np.reshape(current_input, (1, current_input.shape[0], 1)))
        predictions.append(prediction[0, 0])
        current_input = np.append(current_input[1:], prediction, axis=0)

    # Desnormalizar previsões
    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    
    return {
        'station_data_predictions': predictions.flatten().tolist()
    }