from django.urls import path
from .views import ScrapeDataView, StationListView

urlpatterns = [
    # path('api/scrape-data/', ScrapeDataView.as_view(), name='scrape-data'),
    path('scrape/', ScrapeDataView.as_view(), name='scrape_data'),
    path('stations/', StationListView.as_view(), name='station_list'),
]