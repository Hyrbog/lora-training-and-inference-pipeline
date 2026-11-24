# Phase 01: Dataset Curation, Watermark Removal & Dual-Branch Preprocessing

A high-quality LoRA starts with a clean, balanced dataset. No training hyperparameter can fix cropped limbs, watermarks, or inconsistent image quality.

---

## Standardized Folder Architecture

To avoid path errors across Photoshop ExtendScripts, Python utilities, and ComfyUI workflows, this pipeline uses a fixed directory layout inside `ComfyUI/input/`:

```text
ComfyUI/input/
├── DataSetPONY/
│   ├── conFondo/       # 1. Curated & framed images with original background
│   ├── sinFondo/       # 2. Transparent PNG cutouts (Photoshop batch output)
│   └── fondoBlanco/    # 3. Pure white (#FFFFFF) background -> Ready for WD14 Tagger
│
└── DataSetFLUX/
    ├── conFondo/       # 4. Curated images with original background -> Ready for Florence-2
    ├── sinFondo/       # 5. Copied transparent PNG cutouts from Pony branch
    └── Mascaras/       # 6. Binary alpha masks -> Used for masked loss during FLUX training
```

---

## Step 1.1 — Image Selection & Shot Balance (40–50 Images)

Gather **40 to 50 high-resolution images** of the target subject following a strict distribution so the model generalizes well without overfitting to a single pose or background:

* **Framing variety:**
  * ~30% Close-ups (head and shoulders).
  * ~40% Medium / Three-quarter shots.
  * ~30% Full-body shots.
* **Environment & Lighting:** Mix indoor and outdoor scenes with varied lighting conditions so the subject is not baked into a specific background.
* **Distinctive Features (Crucial):** Include **at least 3 close-up detail shots** highlighting unique traits (tattoos, freckles, moles, scars, or specific accessories) so the model learns them accurately.

---

## Step 1.2 — Batch Watermark Removal (`FLUX.1-Fill` 8-Step Pipeline)

Any watermark, logo, or text left in the dataset will be learned by the LoRA and reproduced as artifacts during inference. The included workflow (`workflows/flux_fill_watermark_remover.json`) handles batch watermark removal for both image sequences and extracted video frames.

### Required Models
Place these files in your corresponding ComfyUI `models/` directories before loading the workflow:
* **Diffusion Model (`unet/`):** `fluxfillfp8_v10.safetensors`
* **LoRA (`loras/`):** `Hyper-FLUX.1-dev-8steps-lora.safetensors` *(enables fast 8-step inference)*
* **VAE (`vae/`):** `ae.safetensors`
* **Text Encoders (`clip/`):** `clip_l.safetensors` and `t5xxl_fp8_e4m3fn.safetensors`

### Recommended Base Prompt
```text
Remove watermark, faithfully respecting what lies beneath—whether clothing, a stage set, an object, or organic matter.
```

### Step-by-Step Execution
1. **Prepare frames:** If cleaning a video, extract the frames into `./input/dataset_raw`.
2. **Create mask:** Create a mask covering the exact area where the watermark is located.
3. **Load mask:** Load the mask file into the **`Load Mask`** node.
4. **Set input path:** Point the **`Load Images`** node to your input directory (`./input/dataset_raw`).
5. **Describe area:** Enter or adapt the prompt above to describe what lies beneath the watermark area.
6. **Set batch range:** Adjust the batch range according to your available GPU VRAM (calibrated for **NVIDIA RTX 4090 24GB**).
7. **Reset counter:** Set the **`Lap Counter`** to `0` and its mode to **`Increment`**.
8. **Run:** Queue the prompt and let it process the sequence.

> **Notice:**
> * Occasionally, a few frames (~1–5 out of 100–150 images) may still show faint text remnants. If that happens, inpaint those specific frames individually.
> * *(Optional)* If you are cleaning video frames, reassemble the sequence back into a video using **ComfyUI-VideoHelperSuite**.

---

## Step 1.3 — Framing & Target Resolutions

Manual framing guarantees that key body parts and distinctive traits remain properly composed without accidental head or limb crops. Once framed, batch-resize images into matched orientation pairs to minimize bucket fragmentation during training:

| Tier / Use Case | Portrait (Vertical) | Landscape (Horizontal) | Aspect Ratio | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Master High-Res** | `1634 x 2440` | `2440 x 1634` | ~2:3 | High-detail master dataset. Ostris AI-Toolkit automatically assigns optimal training buckets without losing detail. |
| **Standard / Pony XL** | `840 x 1200` | `1200 x 840` | ~7:10 | Native ratio calibrated for **Pony V6 XL** base generation followed by **Flux** refinement passes. |

### Optional Rescue Step: Batch AI Upscaling (`comfyui_batch_upscaler.json`)
If a source photo lacks sharpness or resolution, run it through `workflows/comfyui_batch_upscaler.json` *before* final framing. It uses **WD14 Tagger** (`wd_eva02-large-tagger-v3`) to detect image content and concatenates the quality boost prompt (`8k uhd, raw, dslr, detailed`) using `cyberrealisticPony_v180_fp32_Coreshift.safetensors` and `4x-UltraSharp.pth`.

---

## Step 1.4 — Dual-Branch Background & Mask Automation

Once all curated images are placed in `DataSetPONY/conFondo/` (and copied to `DataSetFLUX/conFondo/`), execute the three scripts in order:

1. **Extract Transparent Cutouts (`scripts/01_remove_bg_photoshop.jsx`):**
   * Run inside Adobe Photoshop (`File -> Scripts -> Browse...`).
   * Silently isolates the subject using AI `autoCutout`, purges history/clipboard per image to prevent RAM bloat, and exports lossless PNGs to `DataSetPONY/sinFondo/`.
2. **Generate Studio White Backgrounds for Pony (`scripts/02_add_white_bg_pony.jsx`):**
   * Run inside Adobe Photoshop.
   * Reads `DataSetPONY/sinFondo/`, places a pure `#FFFFFF` layer behind the subject, flattens, and saves to `DataSetPONY/fondoBlanco/` (ready for **WD14 Tagger**).
3. **Generate Binary Alpha Masks for FLUX (`scripts/03_generate_flux_masks.py`):**
   * Copy the transparent PNGs from `DataSetPONY/sinFondo/` into `DataSetFLUX/sinFondo/`.
   * Run `python scripts/03_generate_flux_masks.py`.
   * Extracts the alpha channel into grayscale binary masks inside `DataSetFLUX/Mascaras/` so **Ostris AI-Toolkit** focuses training loss strictly on the subject while preserving natural background context from `DataSetFLUX/conFondo/` (captioned via **Florence-2**).

---

## Troubleshooting Common Dataset Issues

* **Blurry or low-res source photos:** Run them through `workflows/comfyui_batch_upscaler.json` *before* framing; never upscale after training.
* **Too many buckets created by the trainer:** Ensure all images strictly match one of the target pairs (`1634x2440` / `2440x1634` or `840x1200` / `1200x840`).
* **Out of Memory (OOM) during batch watermark removal:** Lower the batch size in Step 1.2; `fluxfillfp8_v10` + `t5xxl_fp8` runs smoothly on 24GB VRAM (RTX 4090) when batched properly.
* **Photoshop memory buildup on large batches:** Both `.jsx` scripts include `app.purge()` calls after every image; if processing 200+ high-res frames, run in batches of 100.

---

## Next Step
Once both branches (`DataSetPONY/fondoBlanco` and `DataSetFLUX/conFondo` + `Mascaras`) are ready, proceed to **[Phase 02: Auto-Captioning & Tag Sanitization](../02-auto-captioning/)**.