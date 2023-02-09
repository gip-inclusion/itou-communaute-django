from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User


admin.site.register(User, UserAdmin)


class GroupUserInline(admin.TabularInline):
    model = Group.user_set.through
    list_display = "user_set__email"
    raw_id_fields = ("user",)
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupUserInline]


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
