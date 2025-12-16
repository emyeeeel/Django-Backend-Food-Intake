import os
import csv
import numpy as np
import cv2
import torch
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# YOLO model
from ultralytics import YOLO


# ================================
# YOLO MODEL LOAD (cached)
# ================================
YOLO_MODEL_PATH = r"C:\Users\USER\Documents\Amiel Files\Food Intake\Django-Backend-Food-Intake-\segment\models\best.pt"

yolo_model = None


def load_yolo_model():
    global yolo_model
    if yolo_model is None:
        print("[DEBUG] Loading YOLO model...")
        yolo_model = YOLO(YOLO_MODEL_PATH)
    return yolo_model


# =====================================================
# Helper: Save per-class mask CSVs
# =====================================================
def save_class_mask_csvs(result, model, meal_type):
    """
    Saves one CSV per detected class.
    CSV contains 1 for mask pixels, 0 otherwise.
    Clears old CSVs first.
    """
    masks_dir = os.path.join(
        settings.MEDIA_ROOT,
        "yolo_output",
        meal_type,
        "masks_csv"
    )
    os.makedirs(masks_dir, exist_ok=True)

    # ✅ Always clear old CSVs first
    for f in os.listdir(masks_dir):
        if f.endswith(".csv"):
            os.remove(os.path.join(masks_dir, f))

    # ❗ Now check if there are any masks
    if result.masks is None or result.boxes is None:
        return {}

    masks = result.masks.data.cpu()          # (N, H, W)
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    class_to_mask = {}

    for idx, class_id in enumerate(class_ids):
        class_name = model.names[class_id]
        binary_mask = (masks[idx] > 0).int()

        if class_name not in class_to_mask:
            class_to_mask[class_name] = binary_mask.clone()
        else:
            class_to_mask[class_name] = torch.logical_or(
                class_to_mask[class_name],
                binary_mask
            ).int()

    saved_paths = {}

    for class_name, mask_tensor in class_to_mask.items():
        csv_path = os.path.join(masks_dir, f"{class_name}.csv")

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(mask_tensor.numpy().tolist())

        saved_paths[class_name] = csv_path

    return saved_paths


import json
import pandas as pd

# ==============================
# YOLO Inference Endpoint
# ==============================
@csrf_exempt
def yolo_segment_view(request, meal_type):
    import traceback

    if meal_type not in ["before", "after"]:
        return JsonResponse({"error": "Invalid meal type. Use /yolo/before or /yolo/after"}, status=400)

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    rgb_file = request.FILES.get("rgb_image")
    depth_csv_file = request.FILES.get("depth_csv")
    raw_weight_str = request.POST.get("raw_weight")

    if not rgb_file or not depth_csv_file or raw_weight_str is None:
        return JsonResponse({"error": "rgb_image, depth_csv, and raw_weight are required"}, status=400)

    try:
        raw_weight = float(raw_weight_str)
    except ValueError:
        return JsonResponse({"error": "raw_weight must be numeric"}, status=400)

    try:
        # ----------------------
        # Save uploads
        # ----------------------
        SEGMENT_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "segment_uploads")
        os.makedirs(SEGMENT_UPLOAD_DIR, exist_ok=True)

        rgb_filename = f"uploaded_rgb_{meal_type}.png"
        rgb_path = os.path.join(SEGMENT_UPLOAD_DIR, rgb_filename)

        depth_filename = f"uploaded_depth_{meal_type}.csv"
        depth_path = os.path.join(SEGMENT_UPLOAD_DIR, depth_filename)

        with open(rgb_path, "wb") as f:
            for chunk in rgb_file.chunks():
                f.write(chunk)
        with open(depth_path, "wb") as f:
            for chunk in depth_csv_file.chunks():
                f.write(chunk)

        # ----------------------
        # YOLO output paths
        # ----------------------
        YOLO_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "yolo_output", meal_type)
        MASKS_WITH_DEPTH_DIR = os.path.join(YOLO_OUTPUT_DIR, "masks_with_depth")
        os.makedirs(YOLO_OUTPUT_DIR, exist_ok=True)
        os.makedirs(MASKS_WITH_DEPTH_DIR, exist_ok=True)

        output_filename = f"segmented_yolo_{meal_type}.png"
        output_image_path = os.path.join(YOLO_OUTPUT_DIR, output_filename)

        # ----------------------
        # Load YOLO model and predict
        # ----------------------
        model = load_yolo_model()
        results = model.predict(
            rgb_path,
            conf=0.30,
            iou=0.5,
            task="segment",
            imgsz=(848, 480),
            augment=True
        )
        result = results[0]

        # Save overlay image
        result.save(filename=output_image_path)

        # Save per-class masks CSV
        mask_csv_paths = save_class_mask_csvs(result, model, meal_type)

        # ----------------------
        # Compute volumes
        # ----------------------
        BASE_HEIGHT_MM = 600.0
        FX = 617.0
        FY = 617.0

        volume_dict = {}
        for class_name, csv_path in mask_csv_paths.items():
            try:
                depth_masked = pd.read_csv(depth_path, header=None).to_numpy()
                mask = pd.read_csv(csv_path, header=None).to_numpy()

                if depth_masked.shape != mask.shape:
                    mask = cv2.resize(mask, (depth_masked.shape[1], depth_masked.shape[0]), interpolation=cv2.INTER_NEAREST)

                depth_masked = depth_masked * mask
                food_pixels = depth_masked > 0
                food_depth = depth_masked[food_pixels]

                if food_depth.size == 0:
                    volume_dict[class_name] = 0.0
                    continue

                heights = np.clip(BASE_HEIGHT_MM - food_depth, 0, None)
                pixel_area_per_pixel = (food_depth ** 2) / (FX * FY)
                volume_per_pixel = heights * pixel_area_per_pixel
                volume_mm3 = np.sum(volume_per_pixel)
                volume_ml = volume_mm3 / 1000.0

                volume_dict[class_name] = float(volume_ml)

            except Exception:
                traceback.print_exc()
                volume_dict[class_name] = None

        # ----------------------
        # Save raw_weight and volumes JSON
        # ----------------------
        with open(os.path.join(YOLO_OUTPUT_DIR, "raw_weight.json"), "w") as f:
            json.dump({"raw_weight": raw_weight}, f)

        with open(os.path.join(YOLO_OUTPUT_DIR, "estimated_volumes.json"), "w") as f:
            json.dump(volume_dict, f)

        # ----------------------
        # Build public URLs
        # ----------------------
        input_image_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{rgb_filename}"
        depth_csv_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{depth_filename}"
        output_image_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}yolo_output/{meal_type}/{output_filename}"
        mask_csv_urls = {
            class_name: f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}yolo_output/{meal_type}/masks_csv/{class_name}.csv"
            for class_name in mask_csv_paths.keys()
        }

        return JsonResponse({
            "status": "success",
            "meal_type": meal_type,
            "input_image_url": input_image_url,
            "depth_csv_url": depth_csv_url,
            "output_image_url": output_image_url,
            "mask_csv_urls": mask_csv_urls,
            "num_classes": len(mask_csv_paths),
            "class_names": list(mask_csv_paths.keys()),
            "mask_count": len(mask_csv_paths),
            "raw_weight": raw_weight,
            "estimated_volumes_ml": volume_dict
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"YOLO inference failed: {str(e)}"}, status=500)


# ==============================
# GET Segmented Results Endpoint
# ==============================
def get_segmented_results(request):
    try:
        response_data = {}

        for meal_type in ["before", "after"]:
            YOLO_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "yolo_output", meal_type)
            output_filename = f"segmented_yolo_{meal_type}.png"
            output_image_path = os.path.join(YOLO_OUTPUT_DIR, output_filename)

            if not os.path.exists(output_image_path):
                response_data[meal_type] = {
                    "segmented_image_url": None,
                    "num_classes": 0,
                    "class_names": [],
                    "raw_weight": None,
                    "estimated_volumes_ml": {}
                }
                continue

            segmented_image_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}yolo_output/{meal_type}/{output_filename}"

            # Load class names from masks CSV folder
            masks_csv_dir = os.path.join(YOLO_OUTPUT_DIR, "masks_csv")
            class_names = sorted([os.path.splitext(f)[0] for f in os.listdir(masks_csv_dir) if f.endswith(".csv")]) \
                if os.path.exists(masks_csv_dir) else []

            # Load raw_weight
            raw_weight_file = os.path.join(YOLO_OUTPUT_DIR, "raw_weight.json")
            raw_weight = None
            if os.path.exists(raw_weight_file):
                with open(raw_weight_file, "r") as f:
                    raw_weight = json.load(f).get("raw_weight")

            # Load estimated volumes
            estimated_volumes = {}
            volumes_file = os.path.join(YOLO_OUTPUT_DIR, "estimated_volumes.json")
            if os.path.exists(volumes_file):
                with open(volumes_file, "r") as f:
                    estimated_volumes = json.load(f)

            response_data[meal_type] = {
                "segmented_image_url": segmented_image_url,
                "num_classes": len(class_names),
                "class_names": class_names,
                "raw_weight": raw_weight,
                "estimated_volumes_ml": estimated_volumes
            }

        return JsonResponse({"status": "success", "results": response_data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



# # -------------------------
# # Segment Upload Folder
# # -------------------------
# SEGMENT_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "segment_uploads")
# os.makedirs(SEGMENT_UPLOAD_DIR, exist_ok=True)

# MASKRCNN_DIR = os.path.join(settings.MEDIA_ROOT, "maskrcnn")
# os.makedirs(MASKRCNN_DIR, exist_ok=True)

# # -------------------------
# # Path to script
# # -------------------------
# PLATE_SCRIPT_PATH = r"C:\Users\USER\Documents\Amiel Files\Segmentation Test\MaskRCNN-Test\samples\custom\food_test.py"

# # -------------------------
# # Conda Environment Interpreter
# # -------------------------
# CONDA_RUN = r"C:\ProgramData\anaconda3\condabin\conda.bat"
# CONDA_ENV_NAME = "segment"


# # =====================================================
# # Segment Endpoint: Save uploaded RGB + Depth CSV
# # =====================================================
# @csrf_exempt
# def segment_view(request, meal_type):
#     if meal_type not in ["before", "after"]:
#         return JsonResponse({"error": "Invalid meal type. Use /segment/before or /segment/after"}, status=400)

#     if request.method != "POST":
#         return JsonResponse({"error": "POST only"}, status=405)

#     rgb_file = request.FILES.get("rgb_image")
#     depth_csv_file = request.FILES.get("depth_csv")

#     if not rgb_file:
#         return JsonResponse({"error": "rgb_image is required"}, status=400)
#     if not depth_csv_file:
#         return JsonResponse({"error": "depth_csv is required"}, status=400)

#     # ------------------------------
#     # FILENAMES BASED ON meal_type
#     # ------------------------------
#     rgb_filename = f"uploaded_rgb_{meal_type}.png"
#     depth_filename = f"uploaded_depth_{meal_type}.csv"

#     rgb_path = os.path.join(SEGMENT_UPLOAD_DIR, rgb_filename)
#     depth_csv_path = os.path.join(SEGMENT_UPLOAD_DIR, depth_filename)

#     # Segmented output folder for this meal_type
#     meal_dir = os.path.join(MASKRCNN_DIR, meal_type)
#     os.makedirs(meal_dir, exist_ok=True)
#     segmented_output_path = os.path.join(meal_dir, f"segmented_output_{meal_type}.png")

#     # Save uploaded files
#     try:
#         with open(rgb_path, "wb") as f:
#             for chunk in rgb_file.chunks():
#                 f.write(chunk)

#         with open(depth_csv_path, "wb") as f:
#             for chunk in depth_csv_file.chunks():
#                 f.write(chunk)

#         # Validate files
#         rgb_image = cv2.imread(rgb_path)
#         if rgb_image is None:
#             return JsonResponse({"error": "Uploaded RGB image is invalid"}, status=400)

#         try:
#             depth_data = np.loadtxt(depth_csv_path, delimiter=",")
#         except Exception:
#             return JsonResponse({"error": "Depth CSV is not valid numeric CSV"}, status=400)

#         # ------------------------------
#         # RUN segmentation script
#         # ------------------------------
#         command = [
#             CONDA_RUN,
#             "run",
#             "-n", CONDA_ENV_NAME,
#             "python",
#             PLATE_SCRIPT_PATH,
#             rgb_path,
#             depth_csv_path,
#             segmented_output_path
#         ]

#         print(f"[DEBUG] Running segmentation script: {command}")

#         process = subprocess.run(
#             command,
#             shell=True,
#             capture_output=True,
#             text=True
#         )

#         if process.returncode != 0:
#             return JsonResponse({
#                 "error": "Segmentation script failed",
#                 "stderr": process.stderr,
#                 "stdout": process.stdout
#             }, status=500)

#         # Build URLs
#         rgb_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{rgb_filename}"
#         depth_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}segment_uploads/{depth_filename}"
#         segmented_url = f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/{meal_type}/segmented_output_{meal_type}.png"

#         # List all mask CSV URLs for this meal_type
#         masks_dir = os.path.join(meal_dir, "masks")
#         mask_urls = []
#         if os.path.exists(masks_dir):
#             for mask_file in sorted(os.listdir(masks_dir)):
#                 mask_urls.append(f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}maskrcnn/{meal_type}/masks/{mask_file}")

#         return JsonResponse({
#             "status": "success",
#             "meal_type": meal_type,
#             "message": f"Segmentation for meal '{meal_type}' completed successfully",

#             "rgb_saved_to": rgb_path,
#             "depth_saved_to": depth_csv_path,
#             "segmented_mask_path": segmented_output_path,

#             "rgb_url": rgb_url,
#             "depth_url": depth_url,
#             "segmented_mask_url": segmented_url,
#             "mask_csv_urls": mask_urls,

#             "rgb_shape": rgb_image.shape,
#             "depth_shape": depth_data.shape,
#         })

#     except Exception as e:
#         return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)



# def get_segmented_results(request):
#     try:
#         response_data = {}

#         YOLO_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "yolo_output")

#         for meal_type in ["before", "after"]:
#             meal_dir = os.path.join(YOLO_OUTPUT_DIR, meal_type)
#             segmented_image_path = os.path.join(meal_dir, f"segmented_yolo_{meal_type}.png")

#             if not os.path.exists(segmented_image_path):
#                 response_data[meal_type] = {
#                     "error": f"No YOLO segmented output found for '{meal_type}'"
#                 }
#                 continue

#             # Optional: Extract class names from YOLO masks if needed
#             # For simplicity, here we just read the class names from the YOLO overlay image metadata if available
#             # If you want exact YOLO class extraction, we could save a JSON during inference and read it here

#             response_data[meal_type] = {
#                 "segmented_image_path": segmented_image_path,
#                 "segmented_image_url": f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}yolo_output/{meal_type}/segmented_yolo_{meal_type}.png",
#                 # Optional placeholders for number of classes and class names
#                 "num_classes": None,
#                 "class_names": [],
#             }

#         return JsonResponse({"status": "success", "results": response_data})

#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)
