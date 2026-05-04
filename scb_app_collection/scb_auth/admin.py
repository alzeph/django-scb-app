"""
scb_auth/admin.py

Enregistrement des modèles scb_auth dans l'administration Django.
Les sections conditionnelles (otp_secret, status_verified) s'adaptent
automatiquement à la configuration SCB_AUTH["OPTIONAL_FIELDS"].
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from scb_auth.conf import scb_config
from scb_auth.models import OtpToken


User = get_user_model()


def _build_fieldsets():
    username_field = scb_config.get("USERNAME_FIELD")
    personal_fields = ["first_name", "last_name"]

    extra_fields = []
    if scb_config.is_field_enabled("status_verified"):
        extra_fields.append("status_verified")

    status_fields = ["is_active", "is_staff", "is_superuser"] + extra_fields

    fieldsets = [
        (None,             {"fields": (username_field, "password")}),
        (_("Informations personnelles"), {"fields": personal_fields}),
        (_("Permissions"),  {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates"),        {"fields": ("last_login", "date_joined")}),
    ]

    if scb_config.is_field_enabled("status_verified"):
        fieldsets.append(
            (_("Vérification"), {"fields": ("status_verified",)})
        )

    if scb_config.is_field_enabled("otp_secret"):
        fieldsets.append(
            (_("OTP"), {"fields": ("otp_secret",)})
        )

    return fieldsets


def _build_list_display():
    base = ["phone_number", "first_name", "last_name", "email", "is_active", "is_staff"]
    if scb_config.is_field_enabled("status_verified"):
        base.append("status_verified")
    return base


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets         = _build_fieldsets()
    list_display      = _build_list_display()
    list_filter       = ["is_staff", "is_active"]
    search_fields     = ["phone_number", "first_name", "last_name", "email"]
    ordering          = ["-date_joined"]
    readonly_fields   = ["last_login", "date_joined"]

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "first_name", "last_name", "password1", "password2"),
        }),
    )


# Enregistrement conditionnel de OtpToken
if scb_config.is_field_enabled("otp_secret"):
    try:
        @admin.register(OtpToken)
        class OtpTokenAdmin(admin.ModelAdmin):
            list_display  = ["user", "created_at", "updated_at"]
            readonly_fields = ["created_at", "updated_at"]
            search_fields = ["user__phone_number"]
    except Exception:
        pass  # OtpToken est un placeholder — pas de table en base