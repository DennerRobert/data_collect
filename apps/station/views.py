from django.shortcuts import render
from django.views.generic import ListView , View
from .utils import save_station_data, scrape_station_data
from .models import Historical_data, Station
from django.http import JsonResponse

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

        return Station.objects.prefetch_related('historical_data').order_by('county','name')