\# Phase 02: Dual-Architecture Auto-Captioning \& Tag Sanitization



Different diffusion architectures interpret text prompts in fundamentally different ways. Using booru tags on FLUX degrades natural prompt adherence, while feeding long prose paragraphs into Pony Diffusion V6 XL dilutes quality tokens.



This phase splits the captioning pipeline into two specialized branches matching each model's text encoder (`T5-XXL + CLIP-L` vs. `CLIP-ViT-L/14`).



\---



\## Folder Structure



```text

02-auto-captioning/

├── README.md

├── scripts/

│   └── clean\_pony\_tags.py                 # Deduplication, hair/gender conflict solver \& score tag injector

└── workflows/

&#x20;   ├── florence2\_flux\_captioner.json      # Natural language VLM captioning for FLUX.1

&#x20;   └── wd14\_pony\_tagger.json              # Structured booru tagging for Pony V6 XL

```



\---



\## Branch A — FLUX.1 Captioning (`Florence-2-large-ft`)



FLUX relies on natural, descriptive English sentences to bind subject traits with complex lighting and environments.



\* \*\*Workflow:\*\* `workflows/florence2\_flux\_captioner.json`

\* \*\*Input / Output Directory:\*\* `./input/DataSetFLUX/conFondo` \*(curated images with original backgrounds)\*



\### Key Node Configuration

\* \*\*Model Loader (`DownloadAndLoadFlorence2Model`):\*\*

&#x20; \* Model: `microsoft/Florence-2-large-ft`

&#x20; \* Precision: `fp16` \*(calibrated for NVIDIA RTX 4090 24GB VRAM)\*

\* \*\*Inference Node (`Florence2Run`):\*\*

&#x20; \* Task: `more\_detailed\_caption`

&#x20; \* `fill\_mask`: `true` | `keep\_model\_loaded`: `true`

&#x20; \* `max\_new\_tokens`: `1024` | `num\_beams`: `3` | `do\_sample`: `false` \*(deterministic output)\*

\* \*\*Trigger Prefix:\*\* Concatenates `"A photo of TRIGGER, "` at the beginning of every generated description.

\* \*\*File Pairing (`Load Image Batch` -> `Save Text File`):\*\* Connects `filename\_text` directly to `filename\_prefix` (`encoding: utf-8`) so every `.txt` file matches its source image filename automatically.



\### Execution Steps

1\. Load `workflows/florence2\_flux\_captioner.json` in ComfyUI.

2\. Replace `TRIGGER` in the text prefix node with your unique subject trigger word.

3\. Set the ComfyUI \*\*Batch Count\*\* in the queue menu to match the exact number of images in `./input/DataSetFLUX/conFondo`.

4\. Click \*\*Queue Prompt\*\*. Verify that every `.png`/`.jpg` now has a paired `.txt` file in the same folder.



\---



\## Branch B — Pony Diffusion V6 XL Tagging (`WD14` + Sanitization)



Pony V6 XL responds best to comma-separated booru tags anchored by quality score prefixes (`score\_9, score\_8\_up...`) and studio lighting suffixes.



\* \*\*Workflow:\*\* `workflows/wd14\_pony\_tagger.json`

\* \*\*Sanitizer Script:\*\* `scripts/clean\_pony\_tags.py`

\* \*\*Input / Output Directory:\*\* `./input/DataSetPONY/fondoBlanco` \*(pure white studio background cutouts from Phase 01)\*



\### Step 2.1 — Raw Tag Extraction (`wd14\_pony\_tagger.json`)

1\. Load `workflows/wd14\_pony\_tagger.json` in ComfyUI.

2\. \*\*WD14 Tagger Settings:\*\*

&#x20;  \* Model: `wd-v1-4-convnextv2-tagger-v2`

&#x20;  \* `threshold`: `0.35` | `character\_threshold`: `0.85`

3\. Ensure `filename\_text` from `Load Image Batch` is wired to `filename\_prefix` in `Save Text File`.

4\. Set the ComfyUI \*\*Batch Count\*\* to match the total image count in `./input/DataSetPONY/fondoBlanco` and click \*\*Queue Prompt\*\*.



\### Step 2.2 — Deterministic Tag Sanitization (`clean\_pony\_tags.py`)

Raw WD14 outputs often introduce conflicting hair colors due to studio highlights, misclassify gender on short/tied hairstyles, or inject unwanted style tags (`illustration`, `monochrome`). Run `scripts/clean\_pony\_tags.py` to clean and structure every `.txt` file automatically:



```bash

\# Using standard Python or ComfyUI / AI-Toolkit embedded Python on Windows:

python 02-auto-captioning/scripts/clean\_pony\_tags.py

```



\#### What the Script Enforces

\* \*\*Prefix Injection:\*\* Prepends `TRIGGER, score\_9, score\_8\_up, score\_7\_up, source\_photorealistic, studio photograph`.

\* \*\*Conflict Resolution:\*\* Eliminates multi-tone hair hallucinations and unifies hair color tags to your configured target (`TARGET\_HAIR\_COLOR`).

\* \*\*Gender Consistency:\*\* Normalizes false `1boy` tags triggered by short or tied hair (`ponytail`, `bun`, `updo`).

\* \*\*Noise Removal \& Suffix:\*\* Strips blacklisted tags and appends `white background, simple background` at the end of every caption.



> \*\*Customizing for Male Subjects or Different Hair Colors:\*\* Edit `TRIGGER\_WORD`, `TARGET\_HAIR\_COLOR`, and the gender normalization block at the top of `scripts/clean\_pony\_tags.py`.



\---



\## Troubleshooting Common Captioning Issues



\* \*\*Trainer fails to find captions (`.txt` names don't match images):\*\* Verify that `filename\_text` on `Load Image Batch` is connected to `filename\_prefix` on `Save Text File` so ComfyUI does not append `\_00001\_` suffixes.

\* \*\*Batch stops after 1 image:\*\* Remember to set the ComfyUI \*\*Queue Batch Count\*\* to the total number of images inside your input folder before running.

\* \*\*Trigger word missing or duplicated:\*\* Run `clean\_pony\_tags.py` only once per dataset pass (or ensure `TRIGGER\_WORD` matches the prefix used in ComfyUI, as the script automatically deduplicates it).



\---



\## Next Step

With paired, sanitized captions ready for both branches (`DataSetFLUX` and `DataSetPONY`), proceed to \*\*\[Phase 03: LoRA Training Configurations (Ostris AI-Toolkit)](../03-ostris-training-configs/)\*\*.

