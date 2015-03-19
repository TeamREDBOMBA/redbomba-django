from django.contrib import admin

# Register your models here.
from redbomba.main.models import GlobalCard, PrivateCard, Post, PostImage, PostReply, PostSmile, Tag, Follow, NewsFeed


class GlobalCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','con','src','focus_x','focus_y','date_updated')

class PrivateCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','contype','con','date_updated')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'date_updated', 'video')

class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'src')

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class PostReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_updated', 'content', 'post')

class PostSmileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'fuser', 'tuser')

class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'post', 'date_updated', 'publisher', 'reason')

admin.site.register(GlobalCard, GlobalCardAdmin)
admin.site.register(PrivateCard, PrivateCardAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostImage, PostImageAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(PostReply, PostReplyAdmin)
admin.site.register(PostSmile, PostSmileAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(NewsFeed, NewsFeedAdmin)