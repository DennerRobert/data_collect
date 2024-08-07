from django.urls import path, include

from .views import AddHistoricalDataView, HistoricalDataViewSet, ScrapeDataView, StationHistoricalDataViewSet, StationListView, StationViewset
from rest_framework.routers import DefaultRouter

urlpatterns = [
    # path('api/scrape-data/', ScrapeDataView.as_view(), name='scrape-data'),
    path('scrape/', ScrapeDataView.as_view(), name='scrape_data'),
    path('stations/', StationListView.as_view(), name='station_list'),
]


# Router api
router = DefaultRouter()
router.register(r'stations', StationViewset, basename='station')
router.register(r'historical_data', HistoricalDataViewSet, basename='historical_data')

urlpatterns = [
    path('', include(router.urls)),
    path('stations/<int:station_pk>/historical_data/', StationHistoricalDataViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('stations/<int:station_pk>/', StationHistoricalDataViewSet.as_view({'get': 'retrieve'})),
    path('stations/<int:station_pk>/add_historical_data/', AddHistoricalDataView.as_view(), name='add-historical-data'),
    ]