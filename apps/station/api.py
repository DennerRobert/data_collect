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
        if self.action == 'create':
            return StationCreateSerializer
        return StationSerializer


class StationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        return handle_station_update(request, pk, partial=False)

    def patch(self, request, pk, format=None):
        return handle_station_update(request, pk, partial=True)
    

class HistoricalDataViewSet(viewsets.ModelViewSet):
    queryset = Historical_data.objects.all()
    serializer_class = HistoricalDataSerializer


class StationHistoricalDataViewSet(viewsets.ViewSet):
    def create(self, request, station_pk=None):
        return handle_create_historical_data(request, station_pk)


class AddHistoricalDataView(APIView):
    def post(self, request, station_pk):
        return handle_create_historical_data(request, station_pk)