import os
import shutil
from PIL import Image

folder_path = "wallpapers"
rejected_folder = "rejected"
whitelist_file = "whitelist.txt"

MIN_WIDTH = 1920
MIN_HEIGHT = 1080
MIN_DPI = 72

if os.path.isfile(whitelist_file):
  with open(whitelist_file, "r") as f:
    whitelist = set(line.strip() for line in f if line.strip())
else:
  whitelist = set()

def move_low_quality_images(folder):
  os.makedirs(rejected_folder, exist_ok=True)

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)

    if not os.path.isfile(file_path) or file_path.startswith(rejected_folder):
      continue

    if filename in whitelist:
      print(f"Whitelisted, keeping {filename}")
      continue

    try:
      with Image.open(file_path) as img:
        width, height = img.size
        dpi = img.info.get("dpi", (72, 72))
        dpi_x, dpi_y = dpi

        too_small = width < MIN_WIDTH or height < MIN_HEIGHT
        low_dpi = dpi_x < MIN_DPI or dpi_y < MIN_DPI

        if too_small or low_dpi:
          print(f"Moving {filename} ({width}x{height}, {dpi_x}x{dpi_y} DPI) → rejected/")
          shutil.move(file_path, os.path.join(rejected_folder, filename))
        else:
          print(f"Keeping {filename} ({width}x{height}, {dpi_x}x{dpi_y} DPI)")

    except Exception as e:
      print(f"Skipping {filename} (not an image or corrupted). Error: {e}")

if __name__ == "__main__":
  move_low_quality_images(folder_path)
