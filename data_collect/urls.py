from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from apps.station.views import ScrapeDataView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('station/', include('apps.station.urls')),
    path('', ScrapeDataView.as_view(), name='home'),
]
