\# End-to-End Local AI LoRA Training \& Multi-Model Inference Pipeline



A production-oriented, modular pipeline for curating datasets, automating dual-architecture captioning, training custom LoRAs (\*\*FLUX.1-dev\*\*, \*\*Pony Diffusion V6 XL\*\*, \*\*Wan 2.1\*\*), and running multi-stage image and video inference locally in \*\*ComfyUI\*\*.



> \*\*Hardware \& Environment Calibration:\*\* All memory profiles, batch sizes, FP8/BF16 quantization settings, and launch scripts in this repository are tuned and stress-tested on a single \*\*NVIDIA RTX 4090 (24GB VRAM)\*\* running Windows with \*\*Visual Studio 2022 C++ Build Tools\*\* and \*\*SageAttention\*\*.



\---



\## Pipeline Architecture Overview



```text

\[ Phase 01: Curation \& Preprocessing ]

&#x20; Raw Images / Video Frames

&#x20;  ├── FLUX.1-Fill (8-Step) Watermark Removal

&#x20;  ├── Photoshop ExtendScript: Silent Subject Cutout -> Studio White BG (#FFFFFF)

&#x20;  └── Python (Pillow): Binary Alpha Mask Extraction

&#x20;         │

&#x20;         ▼

\[ Phase 02: Dual-Branch Auto-Captioning ]

&#x20; ├── FLUX Branch  -> Florence-2-large-ft (Natural Language Descriptions)

&#x20; └── Pony Branch  -> WD14 Tagger + Python Sanitizer (Conflict Solver \& Score Prefix)

&#x20;         │

&#x20;         ▼

\[ Phase 03: LoRA Training (Ostris AI-Toolkit) ]

&#x20; ├── pony\_v6\_xl\_lora.example.yaml   (SDXL: Linear 128 / Conv 8, Dual UNet+TE LR)

&#x20; ├── flux\_dev\_lora.example.yaml     (FLUX: Masked Loss 0.1, FP8 Quantization)

&#x20; └── wan21\_i2v\_lora.example.yaml    (Wan 2.1 14B: Temporal/Style Adapter)

&#x20;         │

&#x20;         ▼

\[ Phase 04: Modular Inference \& Video Synthesis (ComfyUI) ]

&#x20; ├── Master 22-Group rgthree Graph (Pony Base + ReActor -> FLUX + IP-Adapter + ADetailer)

&#x20; ├── Batch Blended Face Model Builder (.safetensors)

&#x20; └── Wan 2.2 14B FP8 Video Generator (15s Clips in \~10 min, 1200x840 / 840x1200)

```



\---



\## Repository Structure



| Folder | Description | Key Technologies |

| :--- | :--- | :--- |

| \*\*\[`01-dataset-curation-and-cleanup/`](./01-dataset-curation-and-cleanup/)\*\* | Watermark removal workflow, target resolution pairs (`1634x2440` / `840x1200`), Photoshop batch background scripts, and binary mask generator. | `FLUX.1-Fill`, `ExtendScript`, `Python`, `Pillow` |

| \*\*\[`02-auto-captioning/`](./02-auto-captioning/)\*\* | Architecture-matched captioning workflows and deterministic Python tag sanitizer (gender normalization, hair conflict resolution, quality tags). | `Florence-2`, `WD14 Tagger`, `Python` |

| \*\*\[`03-ostris-training-configs/`](./03-ostris-training-configs/)\*\* | Sanitized YAML training templates calibrated for 24GB VRAM (`bf16`/`qfloat8`) and architectural notes on mask-weighted loss. | `Ostris AI-Toolkit`, `FLUX.1`, `Pony V6 XL`, `Wan 2.1` |

| \*\*\[`04-comfyui-multi-workflow/`](./04-comfyui-multi-workflow/)\*\* | Master 22-group modular ComfyUI graph, ReActor face-model builder, Wan 2.2 video generator, RTX 4090 launcher, and multi-monitor workspace script. | `ComfyUI`, `rgthree`, `IP-Adapter`, `ADetailer`, `SageAttention` |



\---



\## Key Engineering Highlights



\* \*\*Data Hygiene \& Architecture Alignment:\*\* Separates structured booru tags (sanitized via Python for Pony XL) from natural language descriptions (Florence-2 for FLUX), while using binary alpha masks (`mask\_min\_value: 0.1`) to isolate subject features without losing environmental lighting context.

\* \*\*VRAM \& Kernel Optimization (RTX 4090):\*\* Custom Windows launcher initializes `vcvarsall.bat amd64` so Triton/SageAttention kernels compile cleanly at runtime alongside `--disable-smart-memory` to eliminate model reload overhead.

\* \*\*Ergonomic Modular Control:\*\* Replaces tangled single-purpose graphs with a single `rgthree` Fast Groups Bypasser control panel, boolean `TXT2IMG`/`IMG2IMG` switches, 4-block modular prompt concatenation, and early-cutoff IP-Adapter conditioning (`end\_at: 0.750`).



\---



\## License

Distributed under the \*\*MIT License\*\*. See `LICENSE` for more information.

