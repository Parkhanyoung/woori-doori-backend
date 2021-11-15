from django.urls import path

from .views import DatePostAPIView, PlaceAPIView, DayCommentAPIView, \
                   PostCommentAPIView


app_name='date_post'

urlpatterns = [
    path('posts/', DatePostAPIView.as_view(), name='post'),
    path('places/', PlaceAPIView.as_view(), name='place'),
    path('daycomments/', DayCommentAPIView.as_view(), name='daycomment'),
    path('postcomments/', PostCommentAPIView.as_view(), name='postcomment'),
]