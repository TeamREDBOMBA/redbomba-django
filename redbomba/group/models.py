from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import format

# Create your models here.
from redbomba.home.models import Game


class Group(models.Model):
    name = models.TextField()
    nick = models.TextField()
    leader = models.ForeignKey(User)
    group_icon = models.FileField(
        upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')),
        default="static/img/group/default_icon.png"
    )
    game = models.ForeignKey(Game)
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_member(self):
        if self.id:
            return GroupMember.objects.filter(group=self).order_by("order")

    def __unicode__(self):
        return u'%s' %(self.name)

class GroupMember(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    order = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'[%d] %s (%s)' %(self.id, self.user.username, self.group)