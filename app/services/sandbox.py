# IMPORTANT MVP/DEV ONLY TODO:ISOLATION --DOCKER???-- (MAYBE PYODIDE)

from __future__ import annotations
import os, uuid, subprocess, time, textwrap
from typing import Tuple
from ..config import BaseConfig
from ..extensions import logger
from . import files


def run(parent_id: str, src_path: str, user_code: str) -> Tuple[str, str]:
    result_id   = f"{parent_id}_python_{uuid.uuid4()}"
    result_dir  = os.path.join(BaseConfig.UPLOAD_FOLDER, result_id)
    os.makedirs(result_dir, exist_ok=True)
    result_file = os.path.join(result_dir, "result.png")
    script_file = os.path.join(result_dir, "script.py")

    with open(script_file, "w") as f:
        f.write(_build_script(src_path, result_file, user_code))

    try:
        proc = subprocess.run(
            ["python", script_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        logger.info("Sandbox stdout: %s", proc.stdout.strip())
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())

        if not os.path.exists(result_file):
            raise RuntimeError("Script did not create a result image")

        import cv2
        h, w = cv2.imread(result_file).shape[:2]
        files.image_metadata[result_id] = {
            "width": w, "height": h,
            "file_path": result_file,
            "tiling_complete": False,
            "timestamp": time.time(),
            "parent_id": parent_id,
            "operation": "python_code",
            "code": user_code,
            "output": proc.stdout,
        }
        return result_id, result_file

    except subprocess.TimeoutExpired:
        raise RuntimeError("Execution timed out (30 s)")


# Temporary script
def _build_script(src_path: str, dst_path: str, code: str) -> str:
    return textwrap.dedent(f"""
        import cv2, numpy as np, sys
        img = cv2.imread(r"{src_path}")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # USER INPUT CODE DAAAANGERRRRR
        {code}
        

        try:
            if 'result' in locals() and isinstance(result, np.ndarray):
                if result.ndim == 2:
                    result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
                elif result.shape[2] == 3:
                    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
                cv2.imwrite(r"{dst_path}", result)
            else:
                cv2.imwrite(r"{dst_path}", img)
        except Exception as e:
            cv2.imwrite(r"{dst_path}", img)
            print('Error saving result:', e, file=sys.stderr)
    """)
