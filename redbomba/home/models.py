# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    src = models.FileField(
        upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')),
        default="static/img/home/default_icon.png"
    )
    is_pass_arena = models.IntegerField(default=0)
    is_pass_gamelink = models.IntegerField(default=0)

    def get_gamelink(self):
        if self.user:
            return get_or_none(GameLink,user=self.user)

class Game(models.Model):
    name = models.TextField()
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    is_active = models.IntegerField(default=1)

    def __unicode__(self):
        return u'[%d] %s(active:%d)' %(self.id, self.name, self.is_active)

class GameLink(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    account_id = models.TextField()
    account_name = models.TextField()

    def __unicode__(self):
        return u'[%d] %s (%s)' %(self.id, self.user, self.game)



def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None