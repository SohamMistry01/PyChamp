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
    return render(request, "dsa.html")


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

        # Pre-check for GROQ_API_KEY to give immediate, explicit error log if missing
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if not groq_key:
            err_msg = (
                "GROQ_API_KEY is missing or empty. Please ensure GROQ_API_KEY is configured in "
                "your .env file (e.g., pychamp/.env) or environment variables."
            )
            logger.error("[DSA INVOKE CONFIG ERROR] %s", err_msg)
            print(
                f"\n{'='*25} [DSA CONFIGURATION ERROR] {'='*25}\n"
                f"{err_msg}\n"
                f"{'='*75}\n",
                file=sys.stderr,
                flush=True,
            )
            return JsonResponse({
                "error": err_msg,
                "error_type": "ConfigurationError",
                "topic": topic,
                "detail": err_msg,
            }, status=500)

        # Import here to avoid loading heavy ML libs at Django startup
        from pyeditor.dsa_agent import invoke_dsa_agent

        result = invoke_dsa_agent(topic)
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

