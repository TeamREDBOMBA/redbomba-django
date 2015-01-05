from django.contrib import admin

# Register your models here.
from redbomba.main.models import GlobalCard, PrivateCard


class GlobalCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','con','src','focus_x','focus_y','date_updated')

class PrivateCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','contype','con','date_updated')

admin.site.register(GlobalCard, GlobalCardAdmin)
admin.site.register(PrivateCard, PrivateCardAdmin)