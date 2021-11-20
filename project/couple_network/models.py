from django.db import models
from user.models import Profile


class CoupleRequest(models.Model):
    requestor = models.OneToOneField(Profile, on_delete=models.CASCADE,
                                     related_name='c_request')
    responsor = models.OneToOneField(Profile, on_delete=models.CASCADE,
                                     related_name='c_response')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requestor.nickname} to {self.responsor.nickname}'


class CoupleNet(models.Model):
    members = models.ManyToManyField(Profile, related_name='couple_net')
    created_at = models.DateField(null=True, blank=True)

    def __str__(self):
        couple_name = ''
        for member in self.members.all():
            couple_name += f'{member.nickname}/'
        return couple_name