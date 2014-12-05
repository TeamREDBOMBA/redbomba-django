from django.contrib import admin

# Register your models here.
from redbomba.feed.models import Feed, FeedContents, FeedReply


class FeedContentsInline(admin.StackedInline):
    model = FeedContents
    can_delete = True

class FeedReplyInline(admin.StackedInline):
    model = FeedReply
    can_delete = True

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id','user','date_updated')
    inlines = [FeedContentsInline,FeedReplyInline]

admin.site.register(Feed, FeedAdmin)