from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,
                                related_name='profile')
    nickname = models.CharField(max_length=20)
    gender = models.CharField(max_length=5, choices=(('man', '남자'),
                                                     ('woman', '여자')))
    profile_img = models.ImageField(null=True, blank=True,
                                    upload_to='profile_images/')
    id_code = models.CharField(max_length=255, null=True)
    is_alone = models.BooleanField(default=True)

    def __str__(self):
        return self.nickname
