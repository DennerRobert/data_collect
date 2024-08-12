from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.station.models import Historical_data, Station
from apps.station.serializers import HistoricalDataSerializer, StationCreateSerializer, StationSerializer
from .utils import handle_create_historical_data, handle_station_update


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Returns the serializer class to be used for the current action.

        If the action is 'create', returns StationCreateSerializer.
        Otherwise, returns StationSerializer.
        """
        if self.action == 'create':
            return StationCreateSerializer
        return StationSerializer


class StationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        """
        Handles a PUT request to update a station.

        Args:
            request: The incoming request containing the updated station data.
            pk: The primary key of the station to be updated.
            format: The format of the request data (optional).

        Returns:
            Response: A successful response with the updated station data if the request is valid, otherwise a response with error details.
        """
        return handle_station_update(request, pk, partial=False)

    def patch(self, request, pk, format=None):
        """
        Handles a PATCH request to partially update a station.

        Args:
            request: The incoming request containing the updated station data.
            pk: The primary key of the station to be updated.
            format: The format of the request data (optional).

        Returns:
            Response: A successful response with the updated station data if the request is valid, otherwise a response with error details.
        """
        return handle_station_update(request, pk, partial=True)
    

class HistoricalDataViewSet(viewsets.ModelViewSet):
    queryset = Historical_data.objects.all()
    serializer_class = HistoricalDataSerializer


class StationHistoricalDataViewSet(viewsets.ViewSet):
    def create(self, request, station_pk=None):
        """
        Handles the creation of historical data for a specific station.

        Args:
            request: The incoming request containing historical data to be created.
            station_pk: The primary key of the station for which historical data is being created.

        Returns:
            Response: A successful response with the created historical data if the request is valid, otherwise a response with error details.
        """
        return handle_create_historical_data(request, station_pk)


class AddHistoricalDataView(APIView):
    def post(self, request, station_pk):
        """
        Handles a POST request to create historical data for a specific station.

        Args:
            request: The incoming request containing historical data to be created.
            station_pk: The primary key of the station for which historical data is being created.

        Returns:
            Response: A successful response with the created historical data if the request is valid, otherwise a response with error details.
        """
        return handle_create_historical_data(request, station_pk)