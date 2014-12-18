# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.
from redbomba.arena.models import ArenaBanner, LeagueRound, LeagueTeam, LeagueMatch, LeagueReward, LeagueWish, League


class LeagueRoundInline(admin.StackedInline):
    model = LeagueRound
    can_delete = True

class LeagueRewardInline(admin.StackedInline):
    model = LeagueReward
    can_delete = True

class ArenaBannerAdmin(admin.ModelAdmin):
    list_display = ('id','src','url')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('id','name','host','game','poster','method','start_apply','end_apply','min_team','max_team','date_updated','concept')
    inlines = [LeagueRewardInline, LeagueRoundInline]

class LeagueRoundAdmin(admin.ModelAdmin):
    list_display = ('id','league','round','start','end','bestof','is_finish')

class LeagueTeamAdmin(admin.ModelAdmin):
    list_display = ('id','group','round','feasible_time','date_updated','is_complete')

class LeagueMatchAdmin(admin.ModelAdmin):
    list_display = ('id','game','team_a','team_b','host','state','result','date_match')

class LeagueRewardAdmin(admin.ModelAdmin):
    list_display = ('id','league','name','con')

class LeagueWishAdmin(admin.ModelAdmin):
    list_display = ('id','league','user')

admin.site.register(ArenaBanner, ArenaBannerAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(LeagueRound, LeagueRoundAdmin)
admin.site.register(LeagueTeam, LeagueTeamAdmin)
admin.site.register(LeagueMatch, LeagueMatchAdmin)
admin.site.register(LeagueReward, LeagueRewardAdmin)
admin.site.register(LeagueWish, LeagueWishAdmin)