import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import numpy as np
import cv2

UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "segment_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@csrf_exempt
def segment_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    # -------------------------
    # Validate input
    # -------------------------
    rgb_file = request.FILES.get("rgb_image")
    depth_csv_file = request.FILES.get("depth_csv")

    if rgb_file is None:
        return JsonResponse({"error": "rgb_image is required"}, status=400)

    if depth_csv_file is None:
        return JsonResponse({"error": "depth_csv is required"}, status=400)

    # -------------------------
    # Save files
    # -------------------------
    rgb_path = os.path.join(UPLOAD_DIR, "uploaded_rgb.png")
    depth_csv_path = os.path.join(UPLOAD_DIR, "uploaded_depth.csv")

    # Save RGB
    with open(rgb_path, "wb") as f:
        for chunk in rgb_file.chunks():
            f.write(chunk)

    # Save CSV
    with open(depth_csv_path, "wb") as f:
        for chunk in depth_csv_file.chunks():
            f.write(chunk)

    # -------------------------
    # Verify saved files (optional)
    # -------------------------
    try:
        rgb_image = cv2.imread(rgb_path)
        if rgb_image is None:
            return JsonResponse({"error": "Uploaded RGB image invalid"}, status=400)

        depth_data = np.loadtxt(depth_csv_path, delimiter=",")
    except Exception as e:
        return JsonResponse({"error": f"File load error: {str(e)}"}, status=500)

    # --------------------------------
    # No Mask-RCNN here — just saving
    # --------------------------------
    return JsonResponse({
        "status": "success",
        "message": "Files received and saved",
        "rgb_saved_to": rgb_path,
        "depth_saved_to": depth_csv_path,
        "rgb_shape": rgb_image.shape,
        "depth_shape": depth_data.shape,
    })

from .realsense_capture import (
    capture_realsense_image,
    save_depth_and_rgb,
    telea_inpaint_and_save
)


def capture_view(request):
    """
    Angular will call GET or POST /capture/
    This triggers the RealSense pipeline + Telea inpainting.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Use GET method"}, status=405)

    try:
        depth, color = capture_realsense_image()
        save_depth_and_rgb(depth, color)
        telea_inpaint_and_save()

        return JsonResponse({
            "message": "Capture complete",
            "rgb_image": "rgb_image.png",
            "depth_csv": "inpainted_depth.csv",
            "depth_preview": "inpainted_depth.png",
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)