from django.contrib import admin
from models import *
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = True

class TutorInline(admin.StackedInline):
    model = Tutorial
    max_num = 1
    can_delete = True

class UserAdmin(AuthUserAdmin):
    list_display = ('id','username','email','is_active','date_joined')
    inlines = [UserProfileInline, TutorInline]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','user_icon')

class TutorialAdmin(admin.ModelAdmin):
    list_display = ('id','user','is_pass1')

class ChattingAdmin(admin.ModelAdmin):
    list_display = ('group','user','con','date_updated')

class GlobalFeedAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','con','src','focus_x','focus_y','date_updated')

class PrivateCardAdmin(admin.ModelAdmin):
    list_display = ('id','user','contype','con','date_updated')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('id','ufrom','ufromtype','uto','utotype','feedtype','date_updated')

class FeedContentsAdmin(admin.ModelAdmin):
    list_display = ('id','feed','contype','con')

class ContentsAdmin(admin.ModelAdmin):
    list_display = ('id','uto','utotype','ctype','con')

class FeedReplyAdmin(admin.ModelAdmin):
    list_display = ('id','user','feed','con','date_updated')

class FeedSmileAdmin(admin.ModelAdmin):
    list_display = ('id','feed','user')

class FeedCheckAdmin(admin.ModelAdmin):
    list_display = ('id','user','feed')

class GameAdmin(admin.ModelAdmin):
    list_display = ('id','name','is_active')

class GameLinkAdmin(admin.ModelAdmin):
    list_display = ('id','user','game','name','sid')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','user','action','icon','contents','link','date_read','date_updated')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id','name','nick','leader','group_icon','game','date_updated')

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('id','group','user','order','is_active','date_updated')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('id','name','host','game','level','poster','method','start_apply','end_apply','min_team','max_team','date_updated','concept','rule')

class LeagueRoundAdmin(admin.ModelAdmin):
    list_display = ('id','league','round','start','end','bestof','is_finish')

class LeagueInfoAdmin(admin.ModelAdmin):
    list_display = ('id','name','is_required')

class LeagueTeamAdmin(admin.ModelAdmin):
    list_display = ('id','group','round','feasible_time','date_updated','is_complete')

class LeagueMatchAdmin(admin.ModelAdmin):
    list_display = ('id','game','team_a','team_b','host','state','result','date_match')

class LeagueRewardAdmin(admin.ModelAdmin):
    list_display = ('id','league','name','con')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tutorial, TutorialAdmin)
admin.site.register(Chatting, ChattingAdmin)
admin.site.register(GlobalCard, GlobalFeedAdmin)
admin.site.register(PrivateCard, PrivateCardAdmin)
admin.site.register(Contents, ContentsAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedContents, FeedContentsAdmin)
admin.site.register(FeedReply, FeedReplyAdmin)
admin.site.register(FeedSmile, FeedSmileAdmin)
admin.site.register(FeedCheck, FeedCheckAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(GameLink, GameLinkAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(LeagueRound, LeagueRoundAdmin)
admin.site.register(LeagueInfo, LeagueInfoAdmin)
admin.site.register(LeagueTeam, LeagueTeamAdmin)
admin.site.register(LeagueMatch, LeagueMatchAdmin)
admin.site.register(LeagueReward, LeagueRewardAdmin)