import os
import shutil
import hashlib

folder_path = "wallpapers"
duplicates_folder = "duplicates"

def file_hash(path, chunk_size=8192):
  """Compute SHA-256 hash of a file."""
  hasher = hashlib.sha256()
  with open(path, "rb") as f:
    for chunk in iter(lambda: f.read(chunk_size), b""):
      hasher.update(chunk)
  return hasher.hexdigest()

def move_duplicate_images(folder):
  os.makedirs(duplicates_folder, exist_ok=True)

  seen_hashes = {}

  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)

    if not os.path.isfile(file_path):
      continue

    try:
      h = file_hash(file_path)

      if h in seen_hashes:
        original = seen_hashes[h]
        print(f"Duplicate: {filename} == {original} → duplicates/")
        shutil.move(file_path, os.path.join(duplicates_folder, filename))
      else:
        seen_hashes[h] = filename
        print(f"Unique: {filename}")

    except Exception as e:
      print(f"Skipping {filename}. Error: {e}")

if __name__ == "__main__":
  move_duplicate_images(folder_path)
