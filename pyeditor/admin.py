from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    """Inline editor for UserProfile within the standard User admin page."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = "PyChamp Profile"
    fk_name = "user"
    fields = ("experience_level", "groq_api_key", "bio", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

class CustomUserAdmin(BaseUserAdmin):
    """Extended UserAdmin that displays PyChamp profile information."""
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_experience_level",
        "has_custom_groq_key",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "profile__experience_level")

    @admin.display(description="Experience Level")
    def get_experience_level(self, instance):
        if hasattr(instance, "profile") and instance.profile:
            return instance.profile.get_experience_level_display()
        return "-"

    @admin.display(boolean=True, description="Custom Groq Key")
    def has_custom_groq_key(self, instance):
        if hasattr(instance, "profile") and instance.profile:
            return bool(instance.profile.groq_api_key and instance.profile.groq_api_key.strip())
        return False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Standalone admin panel for UserProfile model."""
    list_display = (
        "user",
        "experience_level",
        "has_custom_groq_key",
        "get_saved_notes_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("experience_level", "created_at")
    search_fields = ("user__username", "user__email", "bio")
    readonly_fields = ("created_at", "updated_at")
    fields = (
        "user",
        "experience_level",
        "groq_api_key",
        "bio",
        "saved_notes",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Saved Notes")
    def get_saved_notes_count(self, instance):
        notes = instance.saved_notes or []
        return f"{len(notes)} topics"

    @admin.display(boolean=True, description="Custom Groq Key")
    def has_custom_groq_key(self, instance):
        return bool(instance.groq_api_key and instance.groq_api_key.strip())

# Re-register UserAdmin with profile inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize Admin Site Branding
admin.site.site_header = "PyChamp Administration"
admin.site.site_title = "PyChamp Admin Portal"
admin.site.index_title = "Welcome to PyChamp Admin Portal"
