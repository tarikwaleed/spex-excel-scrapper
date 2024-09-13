from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from .views import TopClientsView,TopProductsView,SalesStatsView,InvoicesTrendView

urlpatterns = [
    path(route='stats',view=SalesStatsView.as_view()),
    path(route='invoicesTrend',view=InvoicesTrendView.as_view()),
    path(route='products',view=TopProductsView.as_view()),
    path(route='clients',view=TopClientsView.as_view()),
    # path(route='',view=SimpleView.as_view()),
]

