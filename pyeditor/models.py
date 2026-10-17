import re
import shutil
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def sanitize_folder_name(name: str) -> str:
    """Convert any topic name into a safe, filesystem-friendly folder name."""
    clean = re.sub(r"[^\w\s-]", "", name).strip().lower()
    clean = re.sub(r"[-\s]+", "_", clean)
    return clean or "untitled_topic"


class UserProfile(models.Model):
    """
    Extended user profile for PyChamp platform users.
    Stores user preferences and registry of saved DSA notes stored on local disk.
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
    groq_api_key = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Custom Groq API Key for DSA AI Tutor. If empty, platform default from .env is used."
    )
    saved_notes = models.JSONField(
        default=list,
        blank=True,
        help_text="Registry of saved DSA topics, folders, and markdown file references"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} ({self.get_experience_level_display()})"

    def has_groq_access(self) -> bool:
        """
        Check if user is authorized to access the AI DSA Tutor.
        Regular users MUST configure their own personal key in their profile.
        Superusers can use their personal key or fall back to the platform .env key.
        """
        import os
        if self.groq_api_key and self.groq_api_key.strip():
            return True
        if self.user.is_superuser and os.getenv("GROQ_API_KEY", "").strip():
            return True
        return False

    def get_groq_api_key(self) -> str:
        """
        Return effective Groq API key:
        - Regular users: strictly their custom key in profile (no .env fallback).
        - Superusers: their custom key in profile, or .env fallback if profile key is blank.
        """
        import os
        user_key = (self.groq_api_key or "").strip()
        if user_key:
            return user_key
        if self.user.is_superuser:
            return os.getenv("GROQ_API_KEY", "").strip()
        return ""

    @property
    def saved_files(self):
        """Alias for saved_notes to support both naming conventions."""
        return self.saved_notes

    def get_notes_directory(self) -> Path:
        """
        Return the absolute Path to this user's saved notes directory on local disk.
        Creates the directory if it does not yet exist.
        """
        base_dir = Path(settings.BASE_DIR) / "saved_notes" / self.user.username
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    def save_topic_notes(self, topic: str, theory: str, pseudocode: str, code: str) -> dict:
        """
        Save the 3 markdown files (theory.md, pseudocode.md, code.md) in a dedicated
        subfolder named after the topic in this user's local directory.
        Updates the profile's saved_notes registry.
        """
        clean_topic = topic.strip()
        folder_name = sanitize_folder_name(clean_topic)
        user_notes_dir = self.get_notes_directory()
        topic_dir = user_notes_dir / folder_name
        topic_dir.mkdir(parents=True, exist_ok=True)

        # Write markdown files with UTF-8 encoding
        (topic_dir / "theory.md").write_text(theory or "", encoding="utf-8")
        (topic_dir / "pseudocode.md").write_text(pseudocode or "", encoding="utf-8")
        (topic_dir / "code.md").write_text(code or "", encoding="utf-8")

        now_str = timezone.now().strftime("%b %d, %Y • %I:%M %p")
        note_entry = {
            "topic": clean_topic,
            "folder_name": folder_name,
            "relative_path": f"saved_notes/{self.user.username}/{folder_name}",
            "saved_at": now_str,
            "files": {
                "theory": "theory.md",
                "pseudocode": "pseudocode.md",
                "code": "code.md",
            },
        }

        # Update existing record or prepend new record
        existing_index = None
        current_notes = list(self.saved_notes or [])
        for idx, item in enumerate(current_notes):
            if item.get("folder_name") == folder_name:
                existing_index = idx
                break

        if existing_index is not None:
            current_notes[existing_index] = note_entry
        else:
            current_notes.insert(0, note_entry)

        self.saved_notes = current_notes
        self.save(update_fields=["saved_notes", "updated_at"])
        return note_entry

    def delete_topic_notes(self, folder_name: str) -> bool:
        """
        Delete a topic's folder from local disk and remove its entry from saved_notes.
        """
        safe_folder = sanitize_folder_name(folder_name)
        topic_dir = self.get_notes_directory() / safe_folder
        if topic_dir.exists() and topic_dir.is_dir():
            shutil.rmtree(topic_dir, ignore_errors=True)

        current_notes = [n for n in (self.saved_notes or []) if n.get("folder_name") != safe_folder]
        self.saved_notes = current_notes
        self.save(update_fields=["saved_notes", "updated_at"])
        return True

    def get_topic_markdown(self, folder_name: str, file_type: str) -> str:
        """
        Read and return the raw markdown string of a specific file ('theory', 'pseudocode', or 'code').
        """
        safe_folder = sanitize_folder_name(folder_name)
        file_map = {
            "theory": "theory.md",
            "pseudocode": "pseudocode.md",
            "code": "code.md",
        }
        filename = file_map.get(file_type, f"{file_type}.md")
        file_path = self.get_notes_directory() / safe_folder / filename
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
        return ""

