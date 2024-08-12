from django.urls import path, include

from .views import AddHistoricalDataView, HistoricalDataViewSet, ScrapeDataView, StationListView, StationUpdateView, StationViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'stations', StationViewset, basename='stations')

urlpatterns = [
    path('stations/<int:pk>/historical_data/', HistoricalDataViewSet.as_view({'get': 'list', 'post': 'create'}), name='station-historical-data'),
    path('stations/<int:pk>/update/', StationUpdateView.as_view(), name='station-update'),
    path('stations/<int:station_pk>/add_historical_data/', AddHistoricalDataView.as_view(), name='add-historical-data'),
    path('scrape/', ScrapeDataView.as_view(), name='scrape_data'),
    # path('stations/', StationListView.as_view(), name='station_list'),
    path('', include(router.urls)),
]