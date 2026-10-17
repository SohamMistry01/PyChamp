import json
import shutil
from pathlib import Path
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from pyeditor.models import UserProfile, sanitize_folder_name


class SavedNotesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            experience_level="intermediate",
        )

    def tearDown(self):
        # Clean up any test saved_notes folder
        user_notes_dir = self.profile.get_notes_directory()
        if user_notes_dir.exists():
            shutil.rmtree(user_notes_dir, ignore_errors=True)

    def test_sanitize_folder_name(self):
        self.assertEqual(sanitize_folder_name("Binary Search"), "binary_search")
        self.assertEqual(sanitize_folder_name("Merge Sort (O(N log N))"), "merge_sort_on_log_n")
        self.assertEqual(sanitize_folder_name(""), "untitled_topic")

    def test_profile_save_and_retrieve_topic_notes(self):
        topic = "Selection Sort"
        theory = "# Selection Sort\nTheory explanation."
        pseudocode = "function selectionSort(arr)"
        code = "def selection_sort(arr):\n    pass"

        note_entry = self.profile.save_topic_notes(topic, theory, pseudocode, code)

        self.assertEqual(note_entry["topic"], "Selection Sort")
        self.assertEqual(note_entry["folder_name"], "selection_sort")
        self.assertEqual(len(self.profile.saved_notes), 1)

        # Check files exist on disk
        topic_dir = self.profile.get_notes_directory() / "selection_sort"
        self.assertTrue((topic_dir / "theory.md").exists())
        self.assertTrue((topic_dir / "pseudocode.md").exists())
        self.assertTrue((topic_dir / "code.md").exists())

        # Check file content
        self.assertEqual(self.profile.get_topic_markdown("selection_sort", "theory"), theory)
        self.assertEqual(self.profile.get_topic_markdown("selection_sort", "pseudocode"), pseudocode)
        self.assertEqual(self.profile.get_topic_markdown("selection_sort", "code"), code)

    def test_profile_delete_topic_notes(self):
        self.profile.save_topic_notes("Bubble Sort", "theory", "pseudocode", "code")
        self.assertEqual(len(self.profile.saved_notes), 1)
        topic_dir = self.profile.get_notes_directory() / "bubble_sort"
        self.assertTrue(topic_dir.exists())

        self.profile.delete_topic_notes("bubble_sort")
        self.assertEqual(len(self.profile.saved_notes), 0)
        self.assertFalse(topic_dir.exists())

    def test_dsa_save_endpoint(self):
        self.client.login(username="testuser", password="password123")
        payload = {
            "topic": "Quick Sort",
            "theory": "Quick Sort Theory",
            "pseudocode": "Quick Sort Pseudocode",
            "code": "def quick_sort(): pass",
        }
        response = self.client.post(
            reverse("dsa_save"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["note"]["folder_name"], "quick_sort")

        # Test saved_notes view renders saved topic
        notes_res = self.client.get(reverse("saved_notes"))
        self.assertEqual(notes_res.status_code, 200)
        self.assertContains(notes_res, "Quick Sort")

        # Test saved_note_content endpoint
        content_res = self.client.get(
            reverse("saved_note_content") + "?folder=quick_sort&type=theory"
        )
        self.assertEqual(content_res.status_code, 200)
        c_data = content_res.json()
        self.assertTrue(c_data["success"])
        self.assertEqual(c_data["content"], "Quick Sort Theory")

    def test_home_admin_button_visibility(self):
        # 1. Regular user should NOT see the Admin button
        self.client.login(username="testuser", password="password123")
        res_regular = self.client.get(reverse("home"))
        self.assertEqual(res_regular.status_code, 200)
        self.assertNotContains(res_regular, "btn-admin")
        self.assertNotContains(res_regular, reverse("admin:index"))

        # 2. Superuser SHOULD see the Admin button
        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
        )
        self.client.login(username="adminuser", password="adminpassword123")
        res_admin = self.client.get(reverse("home"))
        self.assertEqual(res_admin.status_code, 200)
        self.assertContains(res_admin, "btn-admin")
        self.assertContains(res_admin, reverse("admin:index"))

    def test_home_page_intro_and_modules(self):
        self.client.login(username="testuser", password="password123")
        res = self.client.get(reverse("home"))
        self.assertEqual(res.status_code, 200)
        # Verify intro section with PyChamp description exists
        self.assertContains(res, "platform-intro")
        self.assertContains(res, "About PyChamp")
        self.assertContains(res, "Next-Gen Python &amp; Algorithms Learning Suite")
        # Verify workspace modules section exists below intro
        self.assertContains(res, "workspace-header")
        self.assertContains(res, "Workspace Modules")
        self.assertContains(res, "cards-grid")

    def test_editor_page_navbar_icons(self):
        self.client.login(username="testuser", password="password123")
        res = self.client.get(reverse("editor"))
        self.assertEqual(res.status_code, 200)
        # Verify SVG icons are present in navbar
        self.assertContains(res, "icon icon-nav")
        self.assertContains(res, "icon icon-run")
        self.assertContains(res, "icon icon-user-chip")
        # Verify emojis are NOT present in editor navbar
        self.assertNotContains(res, "🏠")
        self.assertNotContains(res, "📚")
        self.assertNotContains(res, "🧠")
        self.assertNotContains(res, "👤")

    def test_dsa_page_navbar_icons(self):
        self.client.login(username="testuser", password="password123")
        res = self.client.get(reverse("dsa"))
        self.assertEqual(res.status_code, 200)
        # Verify SVG icons are present in navbar
        self.assertContains(res, "icon icon-nav")
        self.assertContains(res, "icon icon-user-chip")
        # Verify navbar emojis are NOT present
        self.assertNotContains(res, "🏠 Home")
        self.assertNotContains(res, "📚 Saved Notes")
        self.assertNotContains(res, "💻 Code Editor")
        self.assertNotContains(res, "user-chip-icon")

    def test_profile_page_icons_and_save_button(self):
        self.client.login(username="testuser", password="password123")
        res = self.client.get(reverse("profile"))
        self.assertEqual(res.status_code, 200)
        # Verify SVG icons are present in navbar & save button
        self.assertContains(res, "icon icon-nav")
        self.assertContains(res, "icon icon-btn")
        self.assertContains(res, "Save Changes")
        # Verify emojis are NOT present in profile navbar & save button
        self.assertNotContains(res, "🏠 Home")
        self.assertNotContains(res, "💾")
        self.assertNotContains(res, "🚀 Advanced")

    def test_saved_notes_page_icons(self):
        self.client.login(username="testuser", password="password123")
        res = self.client.get(reverse("saved_notes"))
        self.assertEqual(res.status_code, 200)
        # Verify SVG icons are present
        self.assertContains(res, "icon icon-nav")
        self.assertContains(res, "icon-badge")
        self.assertContains(res, "icon-search")
        # Verify 📁 folder emoji is preserved
        self.assertContains(res, "Local storage: saved_notes/")
        # Verify navbar/action emojis are NOT present
        self.assertNotContains(res, "🏠 Home")
        self.assertNotContains(res, "📚 Saved Notes")
        self.assertNotContains(res, "🧠 DSA AI Tutor")
        self.assertNotContains(res, "💻 Code Editor")
        self.assertNotContains(res, "🗑️")


class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
        )

    def test_admin_panel_back_to_pychamp_link(self):
        self.client.login(username="adminuser", password="adminpassword123")
        res = self.client.get(reverse("admin:index"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Back to PyChamp")
        self.assertContains(res, reverse("home"))
        self.assertContains(res, "PyChamp Administration")


class UserProfileGroqApiKeyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="keyuser",
            email="keyuser@example.com",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            experience_level="beginner",
        )

    def test_groq_api_key_default_empty(self):
        self.assertEqual(self.profile.groq_api_key, "")

    def test_get_groq_api_key_custom(self):
        self.profile.groq_api_key = "gsk_custom_user_key_123"
        self.profile.save()
        self.assertEqual(self.profile.get_groq_api_key(), "gsk_custom_user_key_123")

    def test_get_groq_api_key_fallback(self):
        import os
        self.profile.groq_api_key = ""
        self.profile.save()
        env_key = os.getenv("GROQ_API_KEY", "")
        self.assertEqual(self.profile.get_groq_api_key(), env_key.strip())

    def test_dsa_agent_key_resolution(self):
        import os
        from pyeditor.dsa_agent import _get_api_key

        # When state has custom api_key
        state_custom = {"topic": "Binary Search", "api_key": "gsk_test_override"}
        self.assertEqual(_get_api_key(state_custom), "gsk_test_override")

        # When state has empty api_key, should fallback to env
        state_empty = {"topic": "Binary Search", "api_key": "  "}
        self.assertEqual(_get_api_key(state_empty), os.getenv("GROQ_API_KEY", "").strip())









