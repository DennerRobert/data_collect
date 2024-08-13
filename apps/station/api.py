from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.station.models import Historical_data, Station
from apps.station.serializers import HistoricalDataSerializer, StationAnalysisSerializer, StationCreateSerializer, StationSerializer
from .utils import analyze_station_data, handle_create_historical_data, handle_station_update
import pandas as pd
from rest_framework.response import Response
from rest_framework import status


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
    

class StationAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to analyze historical data for a specific station.

        Args:
            request: The incoming request containing station ID, start date, and end date.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A successful response with the analyzed data if the request is valid, 
                      otherwise a response with error details or a 404 error if no historical data is available.
        """
        serializer = StationAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            station_id = serializer.validated_data['station_id']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            
            historical_data = Historical_data.objects.filter(
                station_id=station_id,
                datetime__range=[start_date, end_date]
            )
            data = pd.DataFrame(list(historical_data.values('datetime', 'battery')))
            
            if data.empty:
                return Response({'error': 'No historical data available for the selected period.'}, status=status.HTTP_404_NOT_FOUND)
            
            result = analyze_station_data(data)
            
            return Response(result, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)