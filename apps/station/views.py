from django.views.generic import ListView , View
from .utils import save_station_data, scrape_station_data
from .models import Historical_data, Station
from django.http import JsonResponse


class ScrapeDataView(View):
    """
    Handles HTTP GET requests for the ScrapeDataView.
    
    Retrieves station data by calling the scrape_station_data function, 
    then saves the retrieved data by calling the save_station_data function.
    
    Args:
        request: The HTTP request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        A JsonResponse object with a status message and a status code of 200.
    """
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
        """
        Retrieves a queryset of Station objects, prefetching their related Historical_data objects.
        
        Args:
            self: The instance of the class this method belongs to.
        
        Returns:
            A queryset of Station objects with prefetched Historical_data.
        """
        
        return Station.objects.prefetch_related('historical_data')