from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from redbomba.home.models import UserProfile, Game, GameLink
from django.contrib.auth.admin import UserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = True

class UserAdmin(UserAdmin):
    list_display = ('id','username','email','is_active','date_joined')
    inlines = [UserProfileInline]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','src','is_pass_arena','tutorial_phase')

class GameAdmin(admin.ModelAdmin):
    list_display = ('id','name','src','is_active')

class GameLinkAdmin(admin.ModelAdmin):
    list_display = ('id','user','game','account_id','account_name')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(GameLink, GameLinkAdmin)