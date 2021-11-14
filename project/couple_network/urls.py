from django.urls import path

from .views import CoupleRequestAPIView, CoupleNetworkAPIView

app_name = 'couple_network'

urlpatterns = [
    path('request/', CoupleRequestAPIView.as_view(), name='c-request'),
    path('couplenet/', CoupleNetworkAPIView.as_view(), name='c-net'),
]
