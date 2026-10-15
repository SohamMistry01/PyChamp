"""
Views for the DSA AI Tutor feature.
"""

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def dsa_view(request):
    """Render the DSA learning page."""
    return render(request, "dsa.html")


@csrf_exempt
def dsa_invoke(request):
    """
    POST endpoint that accepts a DSA topic, invokes the LangGraph agent
    pipeline, and returns the theory / pseudocode / code as JSON.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        # Accept both form-encoded and JSON bodies
        if request.content_type and "json" in request.content_type:
            body = json.loads(request.body)
            topic = body.get("topic", "").strip()
        else:
            topic = request.POST.get("topic", "").strip()

        if not topic:
            return JsonResponse({"error": "Topic is required."}, status=400)

        # Import here to avoid loading heavy ML libs at Django startup
        from pyeditor.dsa_agent import invoke_dsa_agent

        result = invoke_dsa_agent(topic)
        return JsonResponse({
            "topic": result.get("topic", topic),
            "theory": result.get("theory", ""),
            "pseudocode": result.get("pseudocode", ""),
            "code": result.get("code", ""),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
