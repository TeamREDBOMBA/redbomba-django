from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(User)
    action = models.TextField()
    icon = models.TextField()
    contents = models.TextField()
    link = models.TextField()
    date_read = models.IntegerField(default=-1)
    date_updated = models.DateTimeField(auto_now_add=True)