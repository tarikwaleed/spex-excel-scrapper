from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from .views import InventoryStatusView,InventoryBarChartView

urlpatterns = [
    path(route='',view=InventoryStatusView.as_view()),
    path(route='chart',view=InventoryBarChartView.as_view()),
]

