from django.db import models
from user.models import Profile


class CoupleRequest(models.Model):
    requestor = models.OneToOneField(Profile, on_delete=models.CASCADE,
                                     related_name='c_request')
    responsor = models.OneToOneField(Profile, on_delete=models.CASCADE,
                                     related_name='c_response')
    created_at = models.DateTimeField(auto_now_add=True)


class CoupleNet(models.Model):
    members = models.ManyToManyField(Profile, related_name='couple_net')
    created_at = models.DateField(null=True, blank=True)
