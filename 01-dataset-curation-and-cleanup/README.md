# Phase 01: Dataset Curation, Watermark Removal & Resolution Framing

A high-quality LoRA starts with a clean, balanced dataset. No training hyperparameter can fix cropped limbs, watermarks, or inconsistent image quality.

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
1. **Prepare frames:** If cleaning a video, extract the frames using your preferred tool into `./input/dataset_raw`.
2. **Create mask:** Create a mask covering the exact area where the watermark is located.
3. **Load mask:** Load the mask file into the **`Load Mask`** node.
4. **Set input path:** Point the **`Load Images`** node to your input directory (`./input/dataset_raw`).
5. **Describe area:** Enter or adapt the prompt above to describe what lies beneath the watermark area.
6. **Set batch range:** Adjust the batch range according to your available GPU VRAM.
7. **Reset counter:** Set the **`Lap Counter`** to `0` and its mode to **`Increment`**.
8. **Run:** Queue the prompt and let it process the sequence.

> **Notice:**
> * Occasionally, a few frames (~1–5 out of 100–150 images) may still show faint text remnants. If that happens, inpaint those specific frames individually.
> * *(Optional)* If you are cleaning video frames, reassemble the sequence back into a video using **ComfyUI-VideoHelperSuite**.

---

## Step 1.3 — Manual Framing & Target Resolutions

### Why Manual Framing Instead of Auto-Cropping?
Automated center-crop scripts frequently cut off heads, hands, or feet, forcing a manual review anyway. Framing each image manually guarantees that key body parts and distinctive traits remain properly composed.

### Standard Master Resolutions
Once cleaned, images are framed and batch-resized (via Photoshop batch actions or `workflows/comfyui_batch_upscaler.json`) into consistent aspect ratios to minimize bucket fragmentation during training:

| Orientation | Target Resolution | Aspect Ratio | Use Case |
| :--- | :--- | :--- | :--- |
| **Portrait (Master)** | `1634 x 2440` | ~2:3 | High-detail master dataset. Ostris AI-Toolkit automatically assigns optimal training buckets based on the `.yaml` config without losing detail. |
| **Landscape** | `1200 x 840` | ~10:7 | Native ratio used for **Pony V6 XL** base generation followed by **Flux** refinement passes. |

### Optional Rescue Step: Batch AI Upscaling (`comfyui_batch_upscaler.json`)
When source images are already high resolution, manual framing and standard resizing are enough. However, if a source photo lacks sharpness or resolution, use `workflows/comfyui_batch_upscaler.json` to recover detail before framing:

* **How it works:** Processes an entire input folder automatically, using **WD14 Tagger** to detect image content and concatenating the quality boost prompt: `8k uhd, raw, dslr, detailed`.
* **Required Models:**
  * **Checkpoint (`checkpoints/`):** `cyberrealisticPony_v180_fp32_Coreshift.safetensors`
  * **Upscale Model (`upscale_models/`):** `4x-UltraSharp.pth`
  * **Tagger Model (`wd14_tagger/`):** `wd_eva02-large-tagger-v3`

---

## Troubleshooting Common Dataset Issues

* **Blurry or low-res source photos:** Run them through `workflows/comfyui_batch_upscaler.json` *before* final framing; never upscale after training.
* **Too many buckets created by the trainer:** Ensure all portrait images share the exact `1634x2440` ratio and landscape images share `1200x840`. Mixed arbitrary ratios split training steps unevenly across buckets.
* **Out of Memory (OOM) during batch watermark removal:** Lower the batch size in Step 6; `fluxfillfp8_v10` + `t5xxl_fp8` runs comfortably on 12GB–16GB VRAM when processed in small batches.

---

## Next Step
Once all 40–50 images are clean, framed, and verified, proceed to **[Phase 02: Captioning & Tagging](../02-captioning-and-tagging/)**.
