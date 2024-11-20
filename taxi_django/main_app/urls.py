from django.urls import path

from .views import *

app_name = 'main_app'

urlpatterns = [
    path('stocks/', StockView.as_view()),
    path('stocks/<int:pk>/', StocksDetail.as_view()),
    path('ref-keys/', RefKeyListCreateView.as_view()),
    path('ref-keys/<int:pk>/', RefKeyRetrieveUpdateDestroyView.as_view()),
]