import os
from pathlib import Path
import re
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

IMAGE_DIR = "wallpapers"   # change to your folder
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def clean_filename(name: str) -> str:
    name = re.sub(r'[^a-zA-Z0-9_\- ]', '', name)  # remove weird chars
    return name.strip().replace(" ", "_")[:50]    # keep it short & safe

def describe_image(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=15)
    return processor.decode(out[0], skip_special_tokens=True)

def main():
    for file in Path(IMAGE_DIR).iterdir():
        if file.suffix.lower() in VALID_EXTENSIONS:
            print(f"Processing {file}...")
            try:
                desc = describe_image(str(file))
                safe_name = clean_filename(desc)
                new_path = file.with_name(f"{safe_name}{file.suffix}")

                if not new_path.exists():
                    file.rename(new_path)
                    print(f"Renamed -> {new_path.name}")
                else:
                    print(f"Skipped (duplicate name): {new_path.name}")
            except Exception as e:
                print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    main()
