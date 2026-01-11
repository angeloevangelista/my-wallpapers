import re
from pathlib import Path

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# -------------------------
# Configuration
# -------------------------
IMAGE_DIR = Path("wallpapers")  # change if needed
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

MAX_TOKENS = 15
FILENAME_MAX_LEN = 50

# -------------------------
# Device selection
# -------------------------
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

print(f"Using device: {DEVICE}")

# -------------------------
# Load BLIP model
# -------------------------
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(DEVICE)

model.eval()

# -------------------------
# Helpers
# -------------------------
def clean_filename(name: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_\- ]", "", name)
    return name.strip().replace(" ", "_")[:FILENAME_MAX_LEN]


def describe_image(image_path: Path) -> str:
    with Image.open(image_path) as img:
        image = img.convert("RGB")

    inputs = processor(image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            do_sample=False
        )

    return processor.decode(output[0], skip_special_tokens=True)


# -------------------------
# Main logic
# -------------------------
def main() -> None:
    if not IMAGE_DIR.exists():
        raise FileNotFoundError(f"Directory not found: {IMAGE_DIR}")

    for file in IMAGE_DIR.iterdir():
        if not file.is_file():
            continue

        if file.suffix.lower() not in VALID_EXTENSIONS:
            continue

        print(f"Processing: {file.name}")

        try:
            desc = describe_image(file)
            safe_name = clean_filename(desc)

            if not safe_name:
                print("Skipped (empty caption)")
                continue

            new_path = file.with_name(f"{safe_name}{file.suffix}")

            if new_path.exists():
                print(f"Skipped (duplicate): {new_path.name}")
                continue

            file.rename(new_path)
            print(f"Renamed → {new_path.name}")

        except Exception as e:
            print(f"Error processing {file.name}: {e}")


if __name__ == "__main__":
    main()
