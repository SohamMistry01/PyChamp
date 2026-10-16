from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extended user profile for PyChamp platform users.
    Stores additional user metadata and programming preferences.
    """
    EXPERIENCE_CHOICES = [
        ("beginner", "Beginner (New to Python)"),
        ("intermediate", "Intermediate (Knows basics & functions)"),
        ("advanced", "Advanced (Comfortable with DSA & OOP)"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField(
        blank=True,
        default="",
        help_text="Short bio or learning goals"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="beginner",
        help_text="User's Python / programming experience level"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} ({self.get_experience_level_display()})"
