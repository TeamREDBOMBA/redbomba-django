# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    is_pass_arena = models.IntegerField(default=0)
    is_pass_gamelink = models.IntegerField(default=0)

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None