from django.urls import path

from .views import *

app_name = 'main_app'

urlpatterns = [
    path('create_user/', CreateAdminView.as_view()),
    path('login/', LoginView.as_view()),
    path('get_users/', UserListView.as_view()),
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
    path('saveMessage/', ActiveMessageView.as_view()),
    path('saveMessage/<int:pk>/', ActiveMessageView.as_view()),
    path('get_partners/', PartnerListAPIView.as_view()),
    path('getUser/<int:phone>', UserRetrieveView.as_view()),
    path('delete_user/<int:user_id>/', UserDeleteView.as_view()),
    path("users/<int:chat_id>/", UserDetailView.as_view(), name="user-detail"),
    path('driver-licenses/', DriverLicenseCreateAPIView.as_view(), name='create-driver-license'),
    path('driver-licenses/<int:number>', DriverLicenseDetailView.as_view(), name='driver-license-detail'),
    path('cars/', CarCreateAPIView.as_view(), name='car-create'),
    path('cars/<int:vin_number>/', CarDetailView.as_view(), name='car-detail'),
    path('cars/by-id/<int:chat_id>/', CarDetailByIdView.as_view(), name='car-detail-by-id'),
]