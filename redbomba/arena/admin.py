from django.contrib import admin

# Register your models here.
from redbomba.arena.models import ArenaBanner


class ArenaBannerAdmin(admin.ModelAdmin):
    list_display = ('id','src','url')

admin.site.register(ArenaBanner, ArenaBannerAdmin)