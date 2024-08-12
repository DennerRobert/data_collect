from django.shortcuts import render
from django.views.generic import ListView , View
from apps.station.serializers import HistoricalDataCreateSerializer, HistoricalDataSerializer, StationCreateSerializer, StationSerializer
from .utils import save_station_data, scrape_station_data
from .models import Historical_data, Station
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class ScrapeDataView(View):
    def get(self, request, *args, **kwargs):
        stations = scrape_station_data()
        save_station_data(stations)

        return JsonResponse({'status': 'Scraping and salvaging completed'}, status=200)
    

class StationListView(ListView):
    model = Historical_data
    template_name = 'estacao_list.html'
    context_object_name = 'stations'
    paginate_by = 5

    def get_queryset(self):
        
        return Station.objects.prefetch_related('historical_data')
    

@method_decorator(csrf_exempt, name='dispatch')
class StationViewset(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StationCreateSerializer
        return StationSerializer


class StationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        try:
            station = Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StationCreateSerializer(station, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        try:
            station = Station.objects.get(pk=pk)
        except Station.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StationCreateSerializer(station, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class HistoricalDataViewSet(viewsets.ModelViewSet):
    queryset = Historical_data.objects.all()
    serializer_class = HistoricalDataSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        station_id = self.kwargs.get('station_pk')
        station = Station.objects.get(id=station_id)
        request.data['station'] = station.id
        
        return super().create(request, *args, **kwargs)


class StationHistoricalDataViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, station_pk=None):
        station = Station.objects.get(id=station_pk)
        serializer = HistoricalDataCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for data in serializer.validated_data:
                Historical_data.objects.create(station=station, **data)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddHistoricalDataView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, station_pk):
        station = Station.objects.get(id=station_pk)
        serializer = HistoricalDataCreateSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
            for data in serializer.validated_data:
                Historical_data.objects.create(station=station, **data)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)