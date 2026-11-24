import os

# ============================================================================
# WD14 Booru Tag Sanitizer & Structurer for Pony Diffusion V6 XL
# Part of Phase 02: Auto-Captioning & Tag Sanitization
#
# NOTE ON ADAPTABILITY:
# This default template is configured for a female subject with black hair
# photographed against a pure white studio background.
# To adapt it for a MALE subject or DIFFERENT HAIR COLOR:
#   1. Update TARGET_HAIR_COLOR and HAIR_UNIFICATIONS below.
#   2. Swap the gender normalization rules in Step 2 ("1boy" <-> "1girl").
# ============================================================================

# ==================== CONFIGURATION ====================
DATASET_DIR = "./input/DataSetPONY/fondoBlanco"
TRIGGER_WORD = "TRIGGER"  # Replace with your unique subject trigger word
TARGET_HAIR_COLOR = "black hair"

# Mandatory Pony V6 XL studio quality prefix
QUALITY_TAGS = [
    "score_9",
    "score_8_up",
    "score_7_up",
    "source_photorealistic",
    "studio photograph",
]

# Mandatory studio background suffix
BACKGROUND_TAGS = ["white background", "simple background"]

# Blacklist: remove redundant tags, style noise, and unwanted booru artifacts
BLACKLIST_TAGS = {
    TRIGGER_WORD.lower(),
    "simple background",
    "white background",
    "background",
    "transparent background",
    "pantyhose",
    "hetero",
    "penis",
    "breast focus",
    "armpit hair",
    "pectoral focus",
    "male focus",
    "traditional media",
    "illustration",
    "drawing",
    "monochrome",
    "anime screenshot",
    *QUALITY_TAGS,
}

# Normalize hair color hallucinations caused by studio lighting
HAIR_UNIFICATIONS = {
    "brown hair": TARGET_HAIR_COLOR,
    "blonde hair": TARGET_HAIR_COLOR,
    "white hair": TARGET_HAIR_COLOR,
}
# =======================================================


def process_captions():
    if not os.path.exists(DATASET_DIR):
        print(f"\n[X] Error: Directory '{DATASET_DIR}' does not exist.")
        return

    processed_count = 0

    for filename in os.listdir(DATASET_DIR):
        if filename.endswith(".txt") and filename != "all_captions.txt":
            file_path = os.path.join(DATASET_DIR, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            raw_tags = [t.strip() for t in content.split(",") if t.strip()]

            cleaned_tags = []
            force_female = False
            has_target_hair = False

            # Pass 1: Detect hairstyle triggers and existing target hair tag
            for t in raw_tags:
                t_norm = t.lower().replace("_", " ")

                # Short/tied hairstyles often cause WD14 to misclassify gender
                if t_norm in [
                    "short hair",
                    "updo",
                    "ponytail",
                    "bun",
                    "pixie cut",
                    "hair bun",
                    "twintails",
                ]:
                    force_female = True

                if t_norm == TARGET_HAIR_COLOR:
                    has_target_hair = True

            # Pass 2: Filter noise, resolve hair conflicts, and normalize gender
            for t in raw_tags:
                t_norm = t.lower().replace("_", " ")

                # 1. Strict hair color filter (block multi-tone / conflicting colors)
                if "hair" in t_norm and t_norm != TARGET_HAIR_COLOR:
                    if any(
                        kw in t_norm
                        for kw in ["color", "streak", "two tone", "gradient", "multicolored"]
                    ):
                        continue
                    if t_norm in BLACKLIST_TAGS:
                        continue

                # 2. Gender normalization (fix WD14 misclassifications on short hair)
                if t_norm in ["1boy", "male", "guy", "man", "male focus"]:
                    t_norm = "1girl"
                    force_female = True
                elif t_norm in ["boys", "men"]:
                    t_norm = "girls"
                    force_female = True

                # Skip blacklisted tags
                if t_norm in BLACKLIST_TAGS:
                    continue

                # Apply hair color unification map
                final_tag = HAIR_UNIFICATIONS.get(t_norm, t_norm)

                if final_tag not in cleaned_tags:
                    cleaned_tags.append(final_tag)

            # Pass 3: Enforce subject consistency rules
            if force_female:
                for fem_tag in ["female", "1girl"]:
                    if fem_tag not in cleaned_tags:
                        cleaned_tags.insert(0, fem_tag)
                cleaned_tags = [
                    t for t in cleaned_tags if t not in ["1boy", "male", "guy", "man"]
                ]

            if has_target_hair and TARGET_HAIR_COLOR not in cleaned_tags:
                cleaned_tags.append(TARGET_HAIR_COLOR)

            # Remove background tags from middle block before appending at the end
            cleaned_tags = [t for t in cleaned_tags if t not in BACKGROUND_TAGS]

            # Final structured tag order for Pony V6 XL
            final_tags = [TRIGGER_WORD] + QUALITY_TAGS + cleaned_tags + BACKGROUND_TAGS

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(", ".join(final_tags))

            processed_count += 1

    print("\n[+] Caption sanitization and structuring completed successfully.")
    print(f"[+] Processed {processed_count} .txt files in: {DATASET_DIR}")


if __name__ == "__main__":
    process_captions()