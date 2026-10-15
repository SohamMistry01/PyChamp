from django.http import JsonResponse
from django.shortcuts import render
import subprocess
import tempfile
import os
from django.views.decorators.csrf import csrf_exempt

def editor_view(request):
    return render(request, "editor.html")

@csrf_exempt
def run_code(request):
    if request.method == "POST":
        code = request.POST.get("code", "")
        print("Received code:\n", code)   # debug
        try:
            # Save code to a temporary Python file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as tmpfile:
                tmpfile.write(code)
                tmpfile_path = tmpfile.name

            # Execute file in system command prompt
            result = subprocess.run(
                ["python", tmpfile_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout
            error = result.stderr

            # Clean up temp file
            os.remove(tmpfile_path)

            # If no stdout, but program returned something, capture it
            if not output.strip() and result.returncode == 0:
                output = "Code executed successfully (no print output)."

            return JsonResponse({"output": output, "error": error})
        except Exception as e:
            return JsonResponse({"error": str(e)})
        
