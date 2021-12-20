from django.urls import path

from .views import DatePostAPIView, PlaceAPIView, DayCommentAPIView, \
                   PostCommentAPIView, PostImageAPIView


app_name = 'date_post'

urlpatterns = [
    path('place/', PlaceAPIView.as_view(), name='place'),
    path('post/', DatePostAPIView.as_view(), name='post'),
    path('daycomment/', DayCommentAPIView.as_view(), name='daycomment'),
    path('postcomment/', PostCommentAPIView.as_view(), name='postcomment'),
    path('postimage/', PostImageAPIView.as_view(), name='postimage'),
]
