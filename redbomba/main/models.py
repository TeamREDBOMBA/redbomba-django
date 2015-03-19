# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format
from redbomba.feed.models import Feed

import os

CONTYPE_IN_PRIVATECARD_CHOICES = (
    ('txt', '텍스트'),
    ('img', '이미지'),
    ('mov', '비디오'),
)

class GlobalCard(models.Model) :
    user = models.ForeignKey(User)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    title = models.TextField()
    con = models.TextField()
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')), null=True, blank=True)
    focus_x = models.FloatField(default=0.0)
    focus_y = models.FloatField(default=0.0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "[%d] %s"%(self.id, self.title)

class PrivateCard(models.Model) :
    user = models.ForeignKey(User)
    contype = models.CharField(max_length=3,choices=CONTYPE_IN_PRIVATECARD_CHOICES)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.TextField()


class Post(models.Model):
    user = models.ForeignKey(User)
    date_updated = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    tag = models.ManyToManyField(Tag)
    video = models.URLField(null=True)

    def __unicode__(self):
        return self.content

def get_file_path(self, filename):
    return 'upload/postimage/%d/%s' % (self.post.id, filename)

class PostImage(models.Model):
    post = models.ForeignKey(Post)
    src = models.FileField(upload_to=get_file_path)

class PostSmile(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)

class PostReply(models.Model):
    user = models.ForeignKey(User)
    date_updated = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(Post)


class Follow(models.Model):
    fuser = models.ForeignKey(User, related_name='follow_from')
    tuser = models.ForeignKey(User, related_name='follow_to')

    class Meta:
        unique_together = ('fuser', 'tuser')


class NewsFeed(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriber')
    post = models.ForeignKey(Post)
    date_updated = models.DateTimeField(auto_now=True)
    publisher = models.ForeignKey(User, related_name='publisher')
    reason = models.IntegerField(default=0)
    # reason == 0 : 팔로우 하고 있는 사람들이 발행
    # reason == 1 : 팔로우 하고 있는 사람들이 Smile
    # reason == 2 : 팔로우 하고 있는 사람들이 댓글

    class Meta:
        unique_together = ('subscriber', 'post')


