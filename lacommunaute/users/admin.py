from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from lacommunaute.users.models import User


class UserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "identity_provider", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "identity_provider", "groups")


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
