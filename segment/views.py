import os
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

MASKRCNN_DIR = os.path.join(settings.MEDIA_ROOT, "maskrcnn")
os.makedirs(MASKRCNN_DIR, exist_ok=True)

# -------------------------
# Path to script
# -------------------------
PLATE_SCRIPT_PATH = r"C:\Users\USER\Documents\Amiel Files\Segmentation Test\MaskRCNN-Test\samples\custom\food_test.py"

# -------------------------
# Conda Environment Interpreter
# -------------------------
CONDA_RUN = r"C:\ProgramData\anaconda3\condabin\conda.bat"
CONDA_ENV_NAME = "segment"


# =====================================================
# Segment Endpoint: Save uploaded RGB + Depth CSV
# =====================================================
@csrf_exempt
def segment_view(request, meal_type):
    if meal_type not in ["before", "after"]:
        return JsonResponse({"error": "Invalid meal type. Use /segment/before or /segment/after"}, status=400)

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    rgb_file = request.FILES.get("rgb_image")
    depth_csv_file = request.FILES.get("depth_csv")

    if not rgb_file:
        return JsonResponse({"error": "rgb_image is required"}, status=400)
    if not depth_csv_file:
        return JsonResponse({"error": "depth_csv is required"}, status=400)

    # ------------------------------
    # FILENAMES BASED ON meal_type
    # ------------------------------
    rgb_filename = f"uploaded_rgb_{meal_type}.png"
    depth_filename = f"uploaded_depth_{meal_type}.csv"

    rgb_path = os.path.join(SEGMENT_UPLOAD_DIR, rgb_filename)
    depth_csv_path = os.path.join(SEGMENT_UPLOAD_DIR, depth_filename)

    # Segmented output folder for this meal_type
    meal_dir = os.path.join(MASKRCNN_DIR, meal_type)
    os.makedirs(meal_dir, exist_ok=True)
    segmented_output_path = os.path.join(meal_dir, f"segmented_output_{meal_type}.png")

    # Save uploaded files
    try:
        with open(rgb_path, "wb") as f:
            for chunk in rgb_file.chunks():
                f.write(chunk)

        with open(depth_csv_path, "wb") as f:
            for chunk in depth_csv_file.chunks():
                f.write(chunk)

        # Validate files
        rgb_image = cv2.imread(rgb_path)
        if rgb_image is None:
            return JsonResponse({"error": "Uploaded RGB image is invalid"}, status=400)

        try:
            depth_data = np.loadtxt(depth_csv_path, delimiter=",")
        except Exception:
            return JsonResponse({"error": "Depth CSV is not valid numeric CSV"}, status=400)

        # ------------------------------
        # RUN segmentation script
        # ------------------------------
        command = [
            CONDA_RUN,
            "run",
            "-n", CONDA_ENV_NAME,
            "python",
            PLATE_SCRIPT_PATH,
            rgb_path,
            depth_csv_path,
            segmented_output_path
        ]

        print(f"[DEBUG] Running segmentation script: {command}")

        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            return JsonResponse({
                "error": "Segmentation script failed",
                "stderr": process.stderr,
                "stdout": process.stdout
            }, status=500)

        # Build URLs
        rgb_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{rgb_filename}"
        depth_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{depth_filename}"
        segmented_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/{meal_type}/segmented_output_{meal_type}.png"

        # List all mask CSV URLs for this meal_type
        masks_dir = os.path.join(meal_dir, "masks")
        mask_urls = []
        if os.path.exists(masks_dir):
            for mask_file in sorted(os.listdir(masks_dir)):
                mask_urls.append(f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/{meal_type}/masks/{mask_file}")

        return JsonResponse({
            "status": "success",
            "meal_type": meal_type,
            "message": f"Segmentation for meal '{meal_type}' completed successfully",

            "rgb_saved_to": rgb_path,
            "depth_saved_to": depth_csv_path,
            "segmented_mask_path": segmented_output_path,

            "rgb_url": rgb_url,
            "depth_url": depth_url,
            "segmented_mask_url": segmented_url,
            "mask_csv_urls": mask_urls,

            "rgb_shape": rgb_image.shape,
            "depth_shape": depth_data.shape,
        })

    except Exception as e:
        return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)

 

MASKRCNN_DIR = os.path.join(settings.MEDIA_ROOT, "maskrcnn")

def get_segmented_results(request):
    try:
        response_data = {}

        for meal_type in ["before", "after"]:
            meal_dir = os.path.join(MASKRCNN_DIR, meal_type)
            segmented_image_path = os.path.join(meal_dir, f"segmented_output_{meal_type}.png")
            masks_dir = os.path.join(meal_dir, "masks")

            if not os.path.exists(segmented_image_path):
                response_data[meal_type] = {
                    "error": f"No segmented output found for '{meal_type}'"
                }
                continue

            # Extract class names from mask filenames
            class_names_set = set()
            if os.path.exists(masks_dir):
                for mask_file in os.listdir(masks_dir):
                    # Filename format: mask_1_classname.csv
                    parts = mask_file.split("_")
                    if len(parts) >= 3:
                        class_name_with_ext = "_".join(parts[2:])
                        class_name = os.path.splitext(class_name_with_ext)[0]
                        if class_name != "BG":  # exclude background
                            class_names_set.add(class_name)

            class_names_list = sorted(list(class_names_set))

            response_data[meal_type] = {
                "segmented_image_url": f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/{meal_type}/segmented_output_{meal_type}.png",
                "num_classes": len(class_names_list),
                "class_names": class_names_list
            }

        return JsonResponse({"status": "success", "results": response_data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
