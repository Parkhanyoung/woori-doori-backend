from django.urls import path

from .views import DatePostAPIView, PlaceAPIView, DayCommentAPIView


app_name='date_post'

urlpatterns = [
    path('posts/', DatePostAPIView.as_view(), name='post'),
    path('places/', PlaceAPIView.as_view(), name='place'),
    path('daycomments/', DayCommentAPIView.as_view(), name='place'),
]