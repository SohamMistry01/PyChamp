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
    fields = ("experience_level", "bio", "created_at", "updated_at")
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
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "profile__experience_level")

    @admin.display(description="Experience Level")
    def get_experience_level(self, instance):
        if hasattr(instance, "profile") and instance.profile:
            return instance.profile.get_experience_level_display()
        return "-"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Standalone admin panel for UserProfile model."""
    list_display = ("user", "experience_level", "get_saved_notes_count", "created_at", "updated_at")
    list_filter = ("experience_level", "created_at")
    search_fields = ("user__username", "user__email", "bio")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Saved Notes")
    def get_saved_notes_count(self, instance):
        notes = instance.saved_notes or []
        return f"{len(notes)} topics"

# Re-register UserAdmin with profile inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
