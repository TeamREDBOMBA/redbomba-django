from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format
from redbomba.feed.models import Feed


class GlobalCard(models.Model) :
    user = models.ForeignKey(User)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    title = models.TextField()
    con = models.TextField()
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')), null=True, blank=True)
    focus_x = models.FloatField(default=0.0)
    focus_y = models.FloatField(default=0.0)
    date_updated = models.DateTimeField(auto_now_add=True)