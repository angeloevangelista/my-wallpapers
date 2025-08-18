import os
import shutil
from PIL import Image

folder_path = "wallpapers"
rejected_folder = os.path.join(folder_path, "rejected")

MIN_WIDTH = 2048
MIN_HEIGHT = 1080
MIN_DPI = 150

def move_low_quality_images(folder):
  os.makedirs(rejected_folder, exist_ok=True)

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)

    if not os.path.isfile(file_path) or file_path.startswith(rejected_folder):
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
