import pyrealsense2 as rs
import numpy as np
import cv2
import os

# Ensure media/capture folder exists
MEDIA_CAPTURE_DIR = os.path.join("media", "capture")
os.makedirs(MEDIA_CAPTURE_DIR, exist_ok=True)


def capture_realsense_image(width=848, height=480, fps=30):
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)

    profile = pipeline.start(config)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_sensor.set_option(rs.option.visual_preset, 1.0)

    for _ in range(5):
        pipeline.wait_for_frames()

    frames = pipeline.wait_for_frames()
    align = rs.align(rs.stream.color)
    aligned = align.process(frames)

    depth_frame = aligned.get_depth_frame()
    color_frame = aligned.get_color_frame()

    if not depth_frame or not color_frame:
        pipeline.stop()
        raise RuntimeError("Could not retrieve frames")

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    pipeline.stop()
    return depth_image, color_image


def save_depth_and_rgb(depth_image, color_image):
    rgb_path = os.path.join(MEDIA_CAPTURE_DIR, "rgb_image.png")
    depth_csv_path = os.path.join(MEDIA_CAPTURE_DIR, "depth_image.csv")
    depth_jet_path = os.path.join(MEDIA_CAPTURE_DIR, "depth_image_jet.png")
    mask_path = os.path.join(MEDIA_CAPTURE_DIR, "depth_mask.png")

    cv2.imwrite(rgb_path, color_image)
    np.savetxt(depth_csv_path, depth_image, fmt="%d", delimiter=",")

    mask = np.where(depth_image == 0, 0, 255).astype(np.uint8)
    cv2.imwrite(mask_path, mask)

    valid_mask = depth_image > 0
    if np.any(valid_mask):
        depth_for_viz = depth_image.astype(np.float32)
        valid_depths = depth_for_viz[valid_mask]

        dmin, dmax = np.percentile(valid_depths, [2, 98])
        depth_for_viz = np.clip(depth_for_viz, dmin, dmax)

        depth_norm = cv2.normalize(depth_for_viz, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        depth_eq = cv2.equalizeHist(depth_norm)

        depth_colormap_jet = cv2.applyColorMap(depth_eq, cv2.COLORMAP_JET)
        depth_colormap_jet[depth_image == 0] = (0, 0, 0)
    else:
        depth_colormap_jet = np.zeros((depth_image.shape[0],
                                       depth_image.shape[1], 3), dtype=np.uint8)

    cv2.imwrite(depth_jet_path, depth_colormap_jet)

    return rgb_path, depth_csv_path, depth_jet_path, mask_path


def telea_inpaint_and_save():
    jet_path = os.path.join(MEDIA_CAPTURE_DIR, "depth_image_jet.png")
    mask_path = os.path.join(MEDIA_CAPTURE_DIR, "depth_mask.png")
    inpainted_path = os.path.join(MEDIA_CAPTURE_DIR, "inpainted_depth.png")
    inpaint_csv_path = os.path.join(MEDIA_CAPTURE_DIR, "inpainted_depth.csv")

    img = cv2.imread(jet_path)
    mask_raw = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    mask = cv2.bitwise_not(mask_raw)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    inpainted = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(inpainted_path, inpainted)

    depth_orig = np.loadtxt(os.path.join(MEDIA_CAPTURE_DIR, "depth_image.csv"), delimiter=",")
    valid_mask = depth_orig > 0
    valid_depths = depth_orig[valid_mask]

    dmin, dmax = np.percentile(valid_depths, [2, 98])
    inpaint_gray = cv2.cvtColor(inpainted, cv2.COLOR_BGR2GRAY)
    depth_norm = inpaint_gray.astype(np.float32) / 255.0
    depth_inpaint_numeric = depth_norm * (dmax - dmin) + dmin

    np.savetxt(inpaint_csv_path, depth_inpaint_numeric, fmt="%.2f", delimiter=",")

    return inpainted_path, inpaint_csv_path
