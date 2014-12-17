# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format

# Create your models here.

TYPE_IN_FEEDCONTENTS_CHOICES = (
    ('txt', '텍스트'),
    ('img', '이미지'),
    ('mov', '비디오'),
)

class FeedContents(models.Model):
    type = models.CharField(max_length=3,choices=TYPE_IN_FEEDCONTENTS_CHOICES)
    con = models.TextField()

    def __unicode__(self):
        return u'[%d] %s:%s' %(self.id,self.type,self.con)

class FeedReply(models.Model):
    user = models.ForeignKey(User)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "[%d] %s:%s"%(self.id,self.user,self.con)

class Feed(models.Model):
    user = models.ForeignKey(User)
    con = models.ManyToManyField(FeedContents, null=True, blank=True)
    reply = models.ManyToManyField(FeedReply, null=True, blank=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "[%d]%s"%(self.id,self.user.first_name)