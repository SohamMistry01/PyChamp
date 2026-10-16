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

