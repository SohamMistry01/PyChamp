"""
Views for the DSA AI Tutor feature.
"""

import json
import logging
import os
import sys
import traceback
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Ensure .env is loaded from either pychamp/ or repository root
for _env_candidate in [
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
]:
    if _env_candidate.exists():
        load_dotenv(_env_candidate, override=True)


@login_required(login_url="login")
def dsa_view(request):
    """Render the DSA learning page (protected)."""
    from pyeditor.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    has_api_key = profile.has_groq_access()
    return render(
        request,
        "dsa.html",
        {
            "profile": profile,
            "has_api_key": has_api_key,
        },
    )


@csrf_exempt
def dsa_invoke(request):
    """
    POST endpoint that accepts a DSA topic, invokes the LangGraph agent
    pipeline, and returns the theory / pseudocode / code as JSON.
    Requires an authenticated session.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required. Please sign in."}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    topic = ""
    try:
        # Accept both form-encoded and JSON bodies
        if request.content_type and "json" in request.content_type:
            raw_body = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
            body = json.loads(raw_body)
            topic = body.get("topic", "").strip()
        else:
            topic = request.POST.get("topic", "").strip()

        if not topic:
            logger.warning("[DSA INVOKE] Request rejected: missing 'topic' parameter.")
            return JsonResponse({"error": "Topic is required."}, status=400)

        logger.info("[DSA INVOKE] Starting agent invocation for topic: '%s'", topic)

        # 1. Resolve GROQ_API_KEY with strict enforcement:
        # - Regular users: MUST configure their own key in UserProfile (no .env fallback)
        # - Superusers: can use their own key, or fall back to platform .env key
        from pyeditor.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        effective_key = profile.get_groq_api_key()

        if not effective_key:
            if not request.user.is_superuser:
                err_msg = (
                    "Personal Groq API key required. Each user must configure their own individual "
                    "Groq API key to access and run the AI DSA Tutor."
                )
            else:
                err_msg = (
                    "Groq API key is missing. Please configure your Groq API key in your profile "
                    "or set GROQ_API_KEY in your .env file."
                )
            logger.warning("[DSA INVOKE BLOCKED] %s (user: %s)", err_msg, request.user.username)
            return JsonResponse({
                "error": err_msg,
                "error_type": "ApiKeyRequiredError",
                "needs_key": True,
                "topic": topic,
                "detail": err_msg,
            }, status=403)

        if profile.groq_api_key and profile.groq_api_key.strip():
            logger.info(
                "[DSA INVOKE] Using user profile Groq API key for user '%s'",
                request.user.username,
            )
        else:
            logger.info(
                "[DSA INVOKE] Superuser fallback: using environment GROQ_API_KEY for user '%s'",
                request.user.username,
            )

        # Import here to avoid loading heavy ML libs at Django startup
        from pyeditor.dsa_agent import invoke_dsa_agent

        result = invoke_dsa_agent(topic, api_key=effective_key, user=request.user)
        logger.info("[DSA INVOKE] Successfully completed agent invocation for topic: '%s'", topic)

        return JsonResponse({
            "topic": result.get("topic", topic),
            "theory": result.get("theory", ""),
            "pseudocode": result.get("pseudocode", ""),
            "code": result.get("code", ""),
        })


    except Exception as e:
        tb = traceback.format_exc()
        error_type = type(e).__name__
        error_msg = str(e) or error_type

        # 1. Log using Python's logging system
        logger.error(
            "[DSA INVOKE ERROR] Exception occurred for topic '%s': %s: %s\n%s",
            topic,
            error_type,
            error_msg,
            tb,
        )

        # 2. Print directly to sys.stderr so it appears immediately in the Django runserver terminal
        print(
            f"\n{'='*25} [DSA INVOKE ERROR LOG] {'='*25}\n"
            f"Topic: {topic}\n"
            f"Exception Type: {error_type}\n"
            f"Error Message: {error_msg}\n"
            f"Full Traceback:\n{tb}"
            f"{'='*75}\n",
            file=sys.stderr,
            flush=True,
        )

        # 3. Return full error diagnostics to the client
        return JsonResponse({
            "error": error_msg,
            "error_type": error_type,
            "topic": topic,
            "traceback": tb,
            "detail": f"{error_type}: {error_msg}",
        }, status=500)


@login_required(login_url="login")
@csrf_exempt
def save_groq_key_view(request):
    """
    POST endpoint to save or update the authenticated user's Groq API key
    from the modal window or profile settings.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        if request.content_type and "json" in request.content_type:
            raw_body = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
            data = json.loads(raw_body)
            api_key = data.get("api_key", "").strip()
        else:
            api_key = request.POST.get("api_key", "").strip()

        if not api_key:
            return JsonResponse({"error": "API key cannot be empty. Please paste your Groq API key."}, status=400)

        # Validate that key starts with gsk_
        if not api_key.startswith("gsk_") or len(api_key) < 15:
            return JsonResponse({
                "error": "Invalid Groq API key format. Groq API keys begin with 'gsk_' and are at least 20 characters long."
            }, status=400)

        from pyeditor.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.groq_api_key = api_key
        profile.save(update_fields=["groq_api_key", "updated_at"])

        masked = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 8 else "gsk_****"
        logger.info("[GROQ KEY SAVED] Successfully updated API key for user '%s' (%s)", request.user.username, masked)

        return JsonResponse({
            "success": True,
            "message": "Groq API key saved successfully! Your AI DSA Tutor is now unlocked.",
            "masked_key": masked,
        })

    except Exception as e:
        logger.error("[SAVE GROQ KEY ERROR] %s", traceback.format_exc())
        return JsonResponse({"error": f"Failed to save key: {str(e)}"}, status=500)


@csrf_exempt
def dsa_save_notes(request):
    """
    POST endpoint to save generated DSA markdown content (theory, pseudocode, code)
    into a dedicated subfolder on the user's local machine disk and register it in UserProfile.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required. Please sign in."}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        if request.content_type and "json" in request.content_type:
            raw_body = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
            data = json.loads(raw_body)
        else:
            data = request.POST

        topic = data.get("topic", "").strip()
        theory = data.get("theory", "")
        pseudocode = data.get("pseudocode", "")
        code = data.get("code", "")

        if not topic:
            return JsonResponse({"error": "Topic title is required to save notes."}, status=400)

        from pyeditor.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        note_entry = profile.save_topic_notes(
            topic=topic,
            theory=theory,
            pseudocode=pseudocode,
            code=code,
        )

        logger.info(
            "[DSA SAVE] Saved notes for user '%s' on topic '%s' in folder '%s'",
            request.user.username,
            topic,
            note_entry.get("folder_name"),
        )

        return JsonResponse({
            "success": True,
            "message": f"Successfully saved '{topic}' notes to local machine directory!",
            "note": note_entry,
            "total_saved": len(profile.saved_notes),
        })

    except Exception as e:
        logger.error("[DSA SAVE ERROR] %s", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

