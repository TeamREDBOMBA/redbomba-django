from django.contrib import admin

# Register your models here.
from redbomba.feed.models import Feed, FeedContents, FeedReply

class FeedContentsAdmin(admin.ModelAdmin):
    list_display = ('id','type','con')

class FeedReplyAdmin(admin.ModelAdmin):
    list_display = ('id','user','con','date_updated')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id','user','date_updated')

admin.site.register(FeedContents, FeedContentsAdmin)
admin.site.register(FeedReply, FeedReplyAdmin)
admin.site.register(Feed, FeedAdmin)