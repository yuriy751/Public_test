from pathlib import Path
import tempfile
import numpy as np
import cv2

from program.project_io.save_project import save_images_as_npz
from program.project_io.load_project import _restore_image_bundle


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "src"
        dst = root / "dst"
        src.mkdir()
        dst.mkdir()

        imgs = {
            "a.png": (np.random.rand(32, 32) * 255).astype(np.uint8),
            "b.png": (np.random.rand(16, 20) * 255).astype(np.uint8),
        }

        for name, arr in imgs.items():
            cv2.imwrite(str(src / name), arr)

        save_images_as_npz(src, dst)
        assert (dst / "images_bundle.npz").exists(), "bundle was not created"

        _restore_image_bundle(dst)

        for name, arr in imgs.items():
            restored = cv2.imread(str(dst / name), cv2.IMREAD_UNCHANGED)
            assert restored is not None, f"{name} was not restored"
            assert restored.shape == arr.shape, f"shape mismatch for {name}"

    print("OK: bundle save/restore roundtrip passed")


if __name__ == "__main__":
    main()
