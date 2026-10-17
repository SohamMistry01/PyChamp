import json
import os
import re
import subprocess
import tempfile
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt

from .models import UserProfile



# ── Authentication Views ───────────────────────────────────────────────────

def login_view(request):
    """
    Handle user login via username or email address.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")
        next_url = request.POST.get("next") or request.GET.get("next")

        if not username_or_email or not password:
            messages.error(request, "Please provide both username/email and password.")
            return render(request, "login.html", {"username": username_or_email})

        # Allow user to log in with either username or email
        username_to_auth = username_or_email
        if "@" in username_or_email:
            matched_user = User.objects.filter(email__iexact=username_or_email).first()
            if matched_user:
                username_to_auth = matched_user.username

        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "This account is inactive. Please contact support.")
                return render(request, "login.html", {"username": username_or_email})

            auth_login(request, user)

            # Session expiration: 14 days if remember_me is set, else browser session
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")

            # Validate redirect URL to prevent open redirect vulnerabilities
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid username/email or password.")
            return render(request, "login.html", {"username": username_or_email})

    return render(request, "login.html")


def register_view(request):
    """
    Handle new user registration, profile creation, and auto-login.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        experience_level = request.POST.get("experience_level", "beginner").strip()

        form_data = {
            "full_name": full_name,
            "username": username,
            "email": email,
            "experience_level": experience_level,
        }

        # Validations
        if not username:
            messages.error(request, "Username is required.")
            return render(request, "register.html", {"form_data": form_data})

        if not re.match(r"^[\w.@+-]+$", username):
            messages.error(request, "Username may only contain letters, numbers, and @/./+/-/_ characters.")
            return render(request, "register.html", {"form_data": form_data})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username is already taken. Please choose another.")
            return render(request, "register.html", {"form_data": form_data})

        if not email or "@" not in email or "." not in email:
            messages.error(request, "Please enter a valid email address.")
            return render(request, "register.html", {"form_data": form_data})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email address already exists.")
            return render(request, "register.html", {"form_data": form_data})

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, "register.html", {"form_data": form_data})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html", {"form_data": form_data})

        # Split full name into first and last name
        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create associated UserProfile
        if experience_level not in dict(UserProfile.EXPERIENCE_CHOICES):
            experience_level = "beginner"
        UserProfile.objects.create(user=user, experience_level=experience_level)

        # Log user in
        auth_login(request, user)
        messages.success(request, f"Welcome to PyChamp, {user.username}! Your account has been created.")
        return redirect("home")

    return render(request, "register.html")


def logout_view(request):
    """
    Log out the user and redirect to login page.
    """
    auth_logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("login")


# ── Protected Application Views ───────────────────────────────────────────

@login_required(login_url="login")
def profile_view(request):
    """
    Render user profile and handle bio and experience level updates.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        experience_level = request.POST.get("experience_level", "beginner").strip()
        bio = request.POST.get("bio", "").strip()
        groq_api_key = request.POST.get("groq_api_key", None)

        # Update profile fields
        if experience_level in dict(UserProfile.EXPERIENCE_CHOICES):
            profile.experience_level = experience_level
        profile.bio = bio
        if groq_api_key is not None:
            profile.groq_api_key = groq_api_key.strip()
        profile.save()

        # Update user names if changed
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        messages.success(request, "Your profile has been successfully updated!")
        return redirect("profile")

    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "experience_choices": UserProfile.EXPERIENCE_CHOICES,
        },
    )


@login_required(login_url="login")
def home_view(request):
    """
    Render the PyChamp Home Dashboard featuring the 2x2 modular cards layout.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved_notes_count = len(profile.saved_notes or [])
    has_api_key = profile.has_groq_access()
    return render(
        request,
        "home.html",
        {
            "profile": profile,
            "saved_notes_count": saved_notes_count,
            "has_api_key": has_api_key,
        },
    )


@login_required(login_url="login")
def saved_notes_view(request):
    """
    Render the Saved Notes library screen displaying all locally stored topics
    on the user's machine, with sidebar file navigation and instant markdown preview.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_dir = profile.get_notes_directory()
    raw_notes = list(profile.saved_notes or [])
    verified_notes = []

    for item in raw_notes:
        folder_name = item.get("folder_name", "")
        topic_dir = user_dir / folder_name
        if topic_dir.exists() and topic_dir.is_dir():
            item_copy = dict(item)
            item_copy["has_theory"] = (topic_dir / "theory.md").exists()
            item_copy["has_pseudocode"] = (topic_dir / "pseudocode.md").exists()
            item_copy["has_code"] = (topic_dir / "code.md").exists()
            verified_notes.append(item_copy)

    requested_folder = request.GET.get("topic", "").strip()
    requested_file = request.GET.get("type", "theory").strip().lower()
    if requested_file not in ["theory", "pseudocode", "code"]:
        requested_file = "theory"

    # Select active topic
    active_note = None
    if requested_folder:
        for note in verified_notes:
            if note.get("folder_name") == requested_folder:
                active_note = note
                break

    if not active_note and verified_notes:
        active_note = verified_notes[0]

    # Load initial markdown content for active note
    active_content = ""
    if active_note:
        active_content = profile.get_topic_markdown(
            active_note.get("folder_name"),
            requested_file
        )

    context = {
        "profile": profile,
        "saved_notes": verified_notes,
        "total_saved": len(verified_notes),
        "active_note": active_note,
        "active_folder": active_note.get("folder_name") if active_note else "",
        "active_type": requested_file,
        "active_content": active_content,
    }
    return render(request, "saved_notes.html", context)


@login_required(login_url="login")
def saved_note_content(request):
    """
    Fetch the raw markdown string of a specific file ('theory', 'pseudocode', 'code')
    for a specific topic folder stored on the user's local disk.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    folder_name = request.GET.get("folder", "").strip()
    file_type = request.GET.get("type", "theory").strip().lower()

    if not folder_name:
        return JsonResponse({"error": "Folder name is required."}, status=400)

    if file_type not in ["theory", "pseudocode", "code"]:
        return JsonResponse({"error": "Invalid file type. Must be theory, pseudocode, or code."}, status=400)

    content = profile.get_topic_markdown(folder_name, file_type)

    topic_title = folder_name
    for note in (profile.saved_notes or []):
        if note.get("folder_name") == folder_name:
            topic_title = note.get("topic", folder_name)
            break

    return JsonResponse({
        "success": True,
        "folder_name": folder_name,
        "topic": topic_title,
        "file_type": file_type,
        "content": content,
        "filename": f"{file_type}.md",
    })


@csrf_exempt
@login_required(login_url="login")
def delete_saved_note(request):
    """
    Remove a topic's markdown files and directory from local storage and update UserProfile.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        if request.content_type and "json" in request.content_type:
            data = json.loads(request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body)
        else:
            data = request.POST

        folder_name = data.get("folder_name", "").strip()
        if not folder_name:
            return JsonResponse({"error": "Folder name required."}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.delete_topic_notes(folder_name)

        return JsonResponse({
            "success": True,
            "message": f"Successfully deleted '{folder_name}' notes.",
            "folder_name": folder_name,
            "total_saved": len(profile.saved_notes),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@login_required(login_url="login")
def editor_view(request):
    """Render the code editor workspace (protected)."""
    return render(request, "editor.html")


@csrf_exempt
def run_code(request):
    """
    Execute user-submitted Python code in an isolated subprocess.
    Requires an authenticated session.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required. Please sign in to run code."}, status=401)

    if request.method == "POST":
        code = request.POST.get("code", "")
        try:
            # Save code to a temporary Python file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmpfile:
                tmpfile.write(code)
                tmpfile_path = tmpfile.name

            # Execute file with timeout
            result = subprocess.run(
                ["python", tmpfile_path],
                capture_output=True,
                text=True,
                timeout=5,
            )

            output = result.stdout
            error = result.stderr

            # Clean up temp file
            if os.path.exists(tmpfile_path):
                os.remove(tmpfile_path)

            if not output.strip() and result.returncode == 0:
                output = "Code executed successfully (no print output)."

            return JsonResponse({"output": output, "error": error})
        except subprocess.TimeoutExpired:
            return JsonResponse({"error": "Execution timed out (5s limit exceeded)."})
        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error": "POST request required."}, status=405)
