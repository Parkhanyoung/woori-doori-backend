from django.urls import path

from .views import PublicUserAPIView, UserTokenView, ProfileAPIView, \
                   CheckUserStateAPIView

app_name = 'user'

urlpatterns = [
  path('user/', PublicUserAPIView.as_view(), name='user'),
  path('token/', UserTokenView.as_view(), name='token'),
  path('profile/', ProfileAPIView.as_view(), name='profile'),
  path('check/', CheckUserStateAPIView.as_view(), name='profile'),
]
