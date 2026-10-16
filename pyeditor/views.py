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
        return redirect("editor")

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
            return redirect("editor")
        else:
            messages.error(request, "Invalid username/email or password.")
            return render(request, "login.html", {"username": username_or_email})

    return render(request, "login.html")


def register_view(request):
    """
    Handle new user registration, profile creation, and auto-login.
    """
    if request.user.is_authenticated:
        return redirect("editor")

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
        return redirect("editor")

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

        # Update profile fields
        if experience_level in dict(UserProfile.EXPERIENCE_CHOICES):
            profile.experience_level = experience_level
        profile.bio = bio
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
