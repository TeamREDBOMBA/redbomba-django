from django.db import models

# Create your models here.
from django.utils import timezone
from django.utils.dateformat import format


class ArenaBanner(models.Model):
    src = models.FileField(upload_to='upload/files_%s/'%(format(timezone.localtime(timezone.now()), u'U')))
    url = models.TextField(default='/')