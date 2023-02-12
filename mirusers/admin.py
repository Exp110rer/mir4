from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mirusers.models import Hub, MirUser
from django.utils.translation import gettext_lazy as _


@admin.register(MirUser)
class MirUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'hub')
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "hub")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
