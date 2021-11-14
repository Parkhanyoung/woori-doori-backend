from django.db import models

from user.models import Profile
from couple_network.models import CoupleNet


class Place(models.Model):
    category = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=255)
    visit_count = models.IntegerField(default=1)
    couple = models.ForeignKey(CoupleNet, on_delete=models.CASCADE,
                               related_name='places')
                            

class DatePost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.IntegerField(default=1)
    score = models.IntegerField()
    when = models.DateField()
    couple = models.ForeignKey(CoupleNet, on_delete=models.CASCADE,
                               related_name='posts')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               related_name='posts')
    place = models.ForeignKey(Place, on_delete=models.CASCADE,
                              related_name='posts')

class DayComment(models.Model):
    content = models.TextField()
    when = models.DateField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               related_name='daycomments')
    couple = models.ForeignKey(CoupleNet, on_delete=models.CASCADE,
                               related_name='daycomments')