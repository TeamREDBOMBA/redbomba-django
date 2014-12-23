from django.contrib import admin

# Register your models here.
from redbomba.group.models import GroupMember, Group


class GroupMemberInline(admin.StackedInline):
    model = GroupMember
    can_delete = True

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id','name','nick','leader','group_icon','game','date_updated')
    inlines = [GroupMemberInline]

admin.site.register(Group, GroupAdmin)