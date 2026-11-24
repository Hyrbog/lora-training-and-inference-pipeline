import os
import glob
import sys
import subprocess

# ==================== CONFIGURATION ====================
INPUT_PNG_DIR = "./input/DataSetFLUX/sinFondo"
OUTPUT_MASKS_DIR = "./input/DataSetFLUX/Mascaras"
# =======================================================

# Ensure Pillow is available in embedded Python environments
try:
    from PIL import Image
except ImportError:
    print("Installing 'Pillow' into the current Python environment...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image


def generate_masks():
    if not os.path.exists(OUTPUT_MASKS_DIR):
        os.makedirs(OUTPUT_MASKS_DIR)
        print(f"Created masks directory at: {OUTPUT_MASKS_DIR}")

    images = glob.glob(os.path.join(INPUT_PNG_DIR, "*.png"))

    if not images:
        print(f"No .png images found in: {INPUT_PNG_DIR}")
        return

    print(f"Processing {len(images)} transparent cutouts...")

    for img_path in images:
        filename = os.path.basename(img_path)

        with Image.open(img_path) as img:
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                alpha_channel = img.split()[-1]
                bw_mask = alpha_channel.convert("L")
                output_path = os.path.join(OUTPUT_MASKS_DIR, filename)
                bw_mask.save(output_path)
                print(f"[OK] Mask generated for: {filename}")
            else:
                print(f"[SKIP] {filename} has no alpha transparency channel.")

    print("\nProcess finished! All binary masks are ready for FLUX training.")


if __name__ == "__main__":
    generate_masks()