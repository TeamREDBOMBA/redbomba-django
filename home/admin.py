from django.contrib import admin
from models import *
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

# Register your models here.

class UserProfileInline(admin.StackedInline):
 model = UserProfile
 max_num = 1
 can_delete = True

class UserAdmin(AuthUserAdmin):
  list_display = ('id','username','email','is_active','date_joined')
  inlines = [UserProfileInline]

class UserProfileAdmin(admin.ModelAdmin):
  list_display = ('id','user','user_icon')

class TutorialAdmin(admin.ModelAdmin):
  list_display = ('id','uid','is_pass1')

class FeedAdmin(admin.ModelAdmin):
  list_display = ('id','ufrom','ufromtype','uto','utotype','feedtype','date_updated')
  
class ReplyAdmin(admin.ModelAdmin):
  list_display = ('id','ufrom','fid','date_updated')
  
class ContentsAdmin(admin.ModelAdmin):
  list_display = ('id','uto','utotype','ctype','con')
  
class SmileAdmin(admin.ModelAdmin):
  list_display = ('id','fid','uid')
  
class CheckAdmin(admin.ModelAdmin):
  list_display = ('id','uid','fid')

class GameAdmin(admin.ModelAdmin):
  list_display = ('id','name','is_active')
  
class GameLinkAdmin(admin.ModelAdmin):
  list_display = ('id','uid','game','name','sid')
  
class NotificationAdmin(admin.ModelAdmin):
  list_display = ('id','uid','tablename','contents','date_read','date_updated')

class GroupAdmin(admin.ModelAdmin):
  list_display = ('id','name','nick','uid','group_icon','game','date_updated')
  
class GroupMemberAdmin(admin.ModelAdmin):
  list_display = ('id','gid','uid','order','is_active','date_updated')
  
class LeagueAdmin(admin.ModelAdmin):
  list_display = ('id','name','uid','game','level','method','start_apply','end_apply','min_team','max_team','date_updated')
  
class LeagueRoundAdmin(admin.ModelAdmin):
  list_display = ('id','league_id','round','start','end','bestof','is_finish')
  
class LeagueInfoAdmin(admin.ModelAdmin):
  list_display = ('id','name','is_required')

class LeagueTeamAdmin(admin.ModelAdmin):
  list_display = ('id','group_id','round','feasible_time','date_updated')
  
class LeagueMatchAdmin(admin.ModelAdmin):
  list_display = ('id','game','team_a','team_b','host','state','result','date_match')

class LeagueRewardAdmin(admin.ModelAdmin):
  list_display = ('id','league_id','name','con')
  
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Tutorial, TutorialAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Contents, ContentsAdmin)
admin.site.register(Smile, SmileAdmin)
admin.site.register(Check, CheckAdmin)
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