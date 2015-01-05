# -*- coding: utf-8 -*-
import json
import re
import urllib2
import urlparse

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format
from datetime import datetime
from django.utils.timezone import utc

# Create your models here.
import redbomba

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    src = models.FileField(
        upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')),
        default="default/default_icon.png"
    )
    is_pass_arena = models.IntegerField(default=0)
    is_pass_gamelink = models.IntegerField(default=0)

    def get_gamelink(self):
        if self.user:
            return get_or_none(GameLink,user=self.user)

    def get_group(self,game=None):
        res = []
        if game : groupmember = redbomba.group.models.GroupMember.objects.filter(user=self.user,group__game=game)
        else : groupmember = redbomba.group.models.GroupMember.objects.filter(user=self.user)
        if groupmember :
            for gm in groupmember :
                res.append(gm.group)
            return res
        return []

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
    except Exception as e:
        return None

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def get_json(url) :
    j = urllib2.urlopen(url)
    j_obj = json.load(j)
    return j_obj

def get_time_difference(date_data,arg):
    now = datetime.utcnow().replace(tzinfo=utc)

    if arg == "+" :
        timediff = now - date_data
        timediff = timediff.total_seconds()
        if timediff > 259200:
            return date_data.strftime('%m월 %d일')
        elif timediff > 86400:
            return str(int(timediff/3600/24))+"일 전"
        elif timediff > 3600:
            return str(int(timediff/3600))+"시간 전"
        elif timediff > 60:
            return str(int(timediff/60))+"분 전"
        else :
            return "조금 전"
    else :
        timediff = date_data - now
        timediff = timediff.total_seconds()
        if timediff < 0 :
            return "잠시 후"
        elif timediff < 60:
            return str(int(timediff))+"초 후"
        elif timediff < 3600:
            return str(int(timediff/60))+"분 후"
        elif timediff < 86400:
            return str(int(timediff/3600))+"시간 후"
        else :
            return str(int(timediff/86400))+"일 후"
    return ""