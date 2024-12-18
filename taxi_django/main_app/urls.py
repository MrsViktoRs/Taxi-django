from django.urls import path

from .views import *

app_name = 'main_app'

urlpatterns = [
    path('stocks/', StockView.as_view()),
    path('stocks/<int:pk>/', StocksDetail.as_view()),
    path('ref-keys/', RefKeyListCreateView.as_view()),
    path('ref-keys/<int:pk>/', RefKeyRetrieveUpdateDestroyView.as_view()),
    path('messages/poll/', get_messages, name='get_message'),
    path('all_history/', AppealsHistoryGet.as_view(), name='appeals'),
    path('all_history/<int:pk>/', AppealsView.as_view(), name='appeals-update'),
    path('check_reg/', get_user_status, name='check_reg'),
    path('send_message/', SendMessageView.as_view()),
    path('accept_message/', DeleteMessageView.as_view()),
    path('getUser/<int:phone>', UserRetrieveView.as_view()),
    path('saveMessage/', ActiveMessageView.as_view()),
    path('saveMessage/<int:pk>/', ActiveMessageView.as_view())
]