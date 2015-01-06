from django.contrib import admin

# Register your models here.
from redbomba.head.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','user','action','icon','contents','link','date_read','date_updated')

admin.site.register(Notification, NotificationAdmin)