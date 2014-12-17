from django.contrib import admin

# Register your models here.
from redbomba.main.models import GlobalCard

class GlobalCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','con','src','focus_x','focus_y','date_updated')

admin.site.register(GlobalCard, GlobalCardAdmin)