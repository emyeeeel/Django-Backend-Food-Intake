import os
import sys
import subprocess
import numpy as np
import cv2

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# -------------------------
# Segment Upload Folder
# -------------------------
SEGMENT_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "segment_uploads")
os.makedirs(SEGMENT_UPLOAD_DIR, exist_ok=True)


# -------------------------
# Path to plate_test.py
# -------------------------
PLATE_SCRIPT_PATH = r"C:\Users\USER\Documents\Amiel Files\Segmentation Test\MaskRCNN-Test\samples\custom\plate_test.py"

# -------------------------
# Conda Environment Python (segment env)
# -------------------------
PYTHON_EXECUTABLE = r"C:\Users\USER\anaconda3\envs\segment\python.exe"


# =====================================================
# Segment Endpoint: Save uploaded RGB + Depth CSV
# =====================================================
@csrf_exempt
def segment_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    rgb_file = request.FILES.get("rgb_image")
    depth_csv_file = request.FILES.get("depth_csv")

    if not rgb_file:
        return JsonResponse({"error": "rgb_image is required"}, status=400)
    if not depth_csv_file:
        return JsonResponse({"error": "depth_csv is required"}, status=400)

    # Save uploaded files
    rgb_path = os.path.join(SEGMENT_UPLOAD_DIR, "uploaded_rgb.png")
    depth_csv_path = os.path.join(SEGMENT_UPLOAD_DIR, "uploaded_depth.csv")

    try:
        # Save RGB file
        with open(rgb_path, "wb") as f:
            for chunk in rgb_file.chunks():
                f.write(chunk)

        # Save Depth CSV file
        with open(depth_csv_path, "wb") as f:
            for chunk in depth_csv_file.chunks():
                f.write(chunk)

        # Validate files
        rgb_image = cv2.imread(rgb_path)
        if rgb_image is None:
            return JsonResponse({"error": "Uploaded RGB image is invalid"}, status=400)

        depth_data = np.loadtxt(depth_csv_path, delimiter=",")

        # Build public URLs
        rgb_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/uploaded_rgb.png"
        depth_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/uploaded_depth.csv"

        # ============================================================
        # RUN THE PLATE SEGMENTATION SCRIPT via conda run
        # ============================================================
        try:
            command = [
                r"C:\ProgramData\anaconda3\condabin\conda.bat",  # correct conda path
                "run",
                "-n", "segment",
                "python",
                PLATE_SCRIPT_PATH,
                rgb_path,
                depth_csv_path
            ]

            print(f"[DEBUG] Running Plate Test Script: {command}")

            process = subprocess.run(
                command,
                shell=True,          # must be True on Windows
                capture_output=True,
                text=True
            )

            print("RETURNCODE:", process.returncode)
            print("RAW STDERR:", process.stderr)
            print("RAW STDOUT:", process.stdout)

            if process.returncode != 0:
                return JsonResponse({
                    "error": "Segmentation script failed",
                    "stderr": process.stderr
                }, status=500)

        except Exception as e:
            return JsonResponse({"error": f"Segmentation execution failed: {str(e)}"}, status=500)


        # Final segmented output path
        segmented_output_path = os.path.join(settings.MEDIA_ROOT, "maskrcnn", "segmented_output.png")

        segmented_url = (
            f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/segmented_output.png"
        )

        return JsonResponse({
            "status": "success",
            "message": "Files processed and segmentation complete",

            "rgb_saved_to": rgb_path,
            "depth_saved_to": depth_csv_path,

            "rgb_url": rgb_url,
            "depth_url": depth_url,

            "rgb_shape": rgb_image.shape,
            "depth_shape": depth_data.shape,

            "segmented_mask_path": segmented_output_path,
            "segmented_mask_url": segmented_url,

            "script_stdout": process.stdout,
            "script_stderr": process.stderr,
        })

    except Exception as e:
        return JsonResponse({"error": f"File save/load error: {str(e)}"}, status=500)
