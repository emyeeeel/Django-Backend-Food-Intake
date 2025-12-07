import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import numpy as np
import cv2

from .realsense_capture import (
    capture_realsense_image,
    save_depth_and_rgb,
    telea_inpaint_and_save
)

# -------------------------
# Segment Upload Folder
# -------------------------
SEGMENT_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "segment_uploads")
os.makedirs(SEGMENT_UPLOAD_DIR, exist_ok=True)

# -------------------------
# Capture Output Folder
# -------------------------
CAPTURE_DIR = os.path.join(settings.MEDIA_ROOT, "capture")
os.makedirs(CAPTURE_DIR, exist_ok=True)


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
        with open(rgb_path, "wb") as f:
            for chunk in rgb_file.chunks():
                f.write(chunk)

        with open(depth_csv_path, "wb") as f:
            for chunk in depth_csv_file.chunks():
                f.write(chunk)

        # Optional verification
        rgb_image = cv2.imread(rgb_path)
        if rgb_image is None:
            return JsonResponse({"error": "Uploaded RGB image invalid"}, status=400)

        depth_data = np.loadtxt(depth_csv_path, delimiter=",")

        # Build public URLs
        rgb_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{os.path.basename(rgb_path)}"
        depth_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{os.path.basename(depth_csv_path)}"

        return JsonResponse({
            "status": "success",
            "message": "Files received and saved",
            "rgb_saved_to": rgb_path,
            "depth_saved_to": depth_csv_path,
            "rgb_url": rgb_url,
            "depth_url": depth_url,
            "rgb_shape": rgb_image.shape,
            "depth_shape": depth_data.shape,
        })

    except Exception as e:
        return JsonResponse({"error": f"File save/load error: {str(e)}"}, status=500)


# =====================================================
# Capture Endpoint: Trigger RealSense + Telea Inpaint
# =====================================================
def capture_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Use GET method"}, status=405)

    try:
        # Capture images from RealSense
        depth, color = capture_realsense_image()

        # Save images to capture folder
        rgb_path, depth_csv_path, depth_jet_path, mask_path = save_depth_and_rgb(depth, color)

        # Telea inpainting
        inpainted_path, inpaint_csv_path = telea_inpaint_and_save()

        # Build public URLs
        rgb_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}capture/{os.path.basename(rgb_path)}"
        depth_csv_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}capture/{os.path.basename(inpaint_csv_path)}"
        depth_preview_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}capture/{os.path.basename(inpainted_path)}"

        return JsonResponse({
            "status": "success",
            "message": "Capture complete",
            "rgb_image": rgb_url,
            "depth_csv": depth_csv_url,
            "depth_preview": depth_preview_url
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
