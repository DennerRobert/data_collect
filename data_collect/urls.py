from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.station.views import ScrapeDataView , StationListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('station/', include('apps.station.urls')),
    path('scrape/', ScrapeDataView.as_view(), name='home'),
    path('', StationListView.as_view(), name='station_list'),

    # Autenticação por token // API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('', include('apps.station.urls')),
]
