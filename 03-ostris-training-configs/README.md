\# Phase 03: LoRA Training Configurations (Ostris AI-Toolkit)



All training templates in this directory are calibrated and stress-tested for a single \*\*NVIDIA RTX 4090 (24GB VRAM)\*\* running \*\*Ostris AI-Toolkit\*\*.



To maximize training throughput and prevent VRAM bottlenecks, intermediate preview rendering (`disable\_sampling: true`) is turned off across all jobs, relying on curated datasets from Phase 01 and architecture-matched captions from Phase 02.



\---



\## Folder Structure



```text

03-ostris-training-configs/

├── README.md

├── pony\_v6\_xl\_lora.example.yaml     # SDXL / Pony V6 XL (Studio White-BG Strategy)

├── flux\_dev\_lora.example.yaml       # FLUX.1-dev (Masked Subject + Natural Context)

└── wan21\_i2v\_lora.example.yaml      # Wan 2.1 I2V 14B (Temporal / Style LoRA)

```



\---



\## Architecture Comparison \& Hyperparameters (RTX 4090 24GB)



| Parameter | Pony V6 XL (`sdxl`) | FLUX.1-dev (`flux`) | Wan 2.1 I2V (`14B-480P`) |

| :--- | :--- | :--- | :--- |

| \*\*Network Rank (`linear` / `conv`)\*\* | `128` / `8` | `128` / `16` | `32` / `16` |

| \*\*Learning Rate (UNet / DiT)\*\* | `4.0e-05` | `1.5e-04` (`0.00015`) | `5.0e-05` |

| \*\*Text Encoder Training\*\* | `true` (`1.0e-05`) | `false` (Cached T5) | `false` (Cached) |

| \*\*Quantization / VRAM Mode\*\* | `bf16` (`low\_vram: false`) | `qfloat8` (`low\_vram: true`) | `qfloat8` (`low\_vram: true`) |

| \*\*Masking Strategy\*\* | None (Pure `#FFFFFF` BG) | `mask\_min\_value: 0.1` | None |

| \*\*Batch Size / Total Steps\*\* | `2` / `4,000` steps | `1` / `2,000` steps | `1` / `3,000` steps |

| \*\*Checkpoint Save Interval\*\* | Every `500` steps | Every `500` steps | Every `250` steps |



\---



\## Step-by-Step Execution



\### Step 3.1 — Stage Datasets inside AI-Toolkit

Copy your prepared images, paired `.txt` captions, and masks from Phases 01 and 02 into your local `AI-Toolkit/datasets/` directory using clean naming conventions:



```text

AI-Toolkit/datasets/

├── trigger\_PONY/          # Studio white-background PNGs + sanitized WD14 .txt tags

├── trigger\_FLUX/          # Natural-background images + Florence-2 .txt descriptions

└── trigger\_FLUX\_masks/    # Binary grayscale alpha masks matching trigger\_FLUX filenames

```



\### Step 3.2 — Configure \& Launch Training

1\. Copy the desired `.example.yaml` template into your AI-Toolkit `config/` directory and remove `.example` from the filename.

2\. Replace `TRIGGER` in `name:`, `trigger\_word:`, and `folder\_path:` with your subject's unique trigger token.

3\. For \*\*Pony V6 XL\*\*, verify `model.name\_or\_path` points to your local `.safetensors` checkpoint.

4\. Launch the training job from the AI-Toolkit Web UI or CLI:

&#x20;  ```bash

&#x20;  python run.py config/flux\_dev\_lora.yaml

&#x20;  ```



\---



\## Architectural Note: Video Identity Consistency Without Video LoRAs



While `wan21\_i2v\_lora.example.yaml` is provided for training dedicated style or motion adapters on \*\*Wan 2.1 14B\*\*, modern \*\*Wan 2.2 Image-to-Video (14B High/Low Lighting FP8)\*\* workflows using \*\*First-to-Last-Frame (FLF2V)\*\* conditioning eliminate the need to train subject-specific video LoRAs in production:



\* By feeding high-detail start and end keyframes generated in Phase 04 (Pony base + FLUX refinement) and appending a temporal consistency anchor to the prompt:

&#x20; ```text

&#x20; Facial features and body details remain consistent throughout the scene as it unfolds normally.

&#x20; ```

&#x20; the video model preserves facial geometry, skin details, and clothing natively across the entire clip without extra LoRA overhead.



\---



\## Troubleshooting Training Issues



\* \*\*Memory spikes during FLUX T5-XXL text encoding:\*\* Following recent AI-Toolkit updates, caching large T5 embeddings to disk/RAM can occasionally trigger host memory errors. If this occurs, set `cache\_text\_embeddings: false` and `unload\_text\_encoder: true` under the `train:` block.

\* \*\*Halos or background bleed on FLUX outputs:\*\* Ensure `mask\_min\_value` stays at `0.1` (90% subject loss weight, 10% background lighting context) and verify that mask filenames in `trigger\_FLUX\_masks/` match `trigger\_FLUX/` identically.

\* \*\*Overfitting on Pony V6 XL:\*\* Check intermediate checkpoints saved every `500` steps (`2500`, `3000`, `3500`, `4000`). If poses become rigid at step `4000`, step `3000` or `3500` usually offers the best balance between likeness and prompt flexibility.



\---



\## Next Step

With your trained `.safetensors` LoRAs exported to `./output`, proceed to \*\*\[Phase 04: Modular Multi-Model Inference Workflow (ComfyUI)](../04-comfyui-multi-workflow/)\*\*.

