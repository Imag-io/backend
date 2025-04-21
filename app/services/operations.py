from __future__ import annotations
import os, uuid, cv2, time
from typing import Tuple
from ..config import BaseConfig
from ..extensions import logger
from . import files


def run(parent_id: str, src_path: str,
        operation: str, params: dict) -> Tuple[str, str]:
    #Do {operation} and return (result_id, result_file_path).

    root_id = parent_id.split("_")[0]
    result_id   = f"{root_id}_{operation}_{uuid.uuid4()}"
    result_dir  = os.path.join(BaseConfig.UPLOAD_FOLDER, result_id)
    os.makedirs(result_dir, exist_ok=True)
    result_file = os.path.join(result_dir, "result.png")

    img = cv2.imread(src_path)
    result = _apply(img, operation, params)
    cv2.imwrite(result_file, result)

    h, w = result.shape[:2]
    files.image_metadata[result_id] = {
        "width": w, "height": h,
        "file_path": result_file,
        "tiling_complete": False,
        "timestamp": time.time(),
        "parent_id": parent_id,
        "operation": operation,
        "params": params,
    }
    logger.info("Operation %s → %s", operation, result_id)
    return result_id, result_file


def finish(image_id: str, file_path: str) -> None:
    #Helper: FROM  TO tiler.process_image."""
    from .tiler import process_image
    process_image(image_id, file_path)


# Custom operations TODO: check what are the relevant operations to add/modify
def _apply(img, op, p):
    if op == "grayscale":
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

    if op == "blur":
        k = int(p.get("kernel_size", 5))
        return cv2.GaussianBlur(img, (k, k), 0)

    if op == "edge_detection":
        sigma = float(p.get("sigma", 0.33))
        v = float(p.get("median", None) or cv2.medianBlur(img, 3).mean())
        lower, upper = int(max(0, (1.0 - sigma) * v)), int(min(255, (1.0 + sigma) * v))
        e = cv2.Canny(img, lower, upper)
        return cv2.cvtColor(e, cv2.COLOR_GRAY2BGR)

    if op == "threshold":
        thresh = int(p.get("threshold", 127))
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, out = cv2.threshold(g, thresh, 255, cv2.THRESH_BINARY)
        return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)

    if op == "histogram_equalization":
        yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    raise ValueError(f"Unknown operation: {op}")