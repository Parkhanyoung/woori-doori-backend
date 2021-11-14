from django.db import models
from django.contrib.auth import get_user_model


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                related_name='profile')
    nickname = models.CharField(max_length=20)
    gender = models.CharField(max_length=5, choices=(('man', '남자'),
                                                     ('woman', '여자')))
    profile_img = models.ImageField(null=True)
    id_code = models.CharField(max_length=255, null=True)
    is_alone = models.BooleanField(default=True)
