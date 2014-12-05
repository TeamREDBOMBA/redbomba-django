from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format

# Create your models here.

class Feed(models.Model):
    user = models.ForeignKey(User)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user

class FeedContents(models.Model):
    feed = models.ForeignKey(Feed)
    type = models.CharField(max_length=3)
    con = models.TextField()

    def __unicode__(self):
        return u'[%d] %s(%s):%s' %(self.id,self.feed,self.contype,self.con)

class FeedReply(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(User)
    con = models.TextField()
    date_updated = models.DateTimeField(auto_now_add=True)