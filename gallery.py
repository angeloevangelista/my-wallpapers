from flask import Flask, send_from_directory, jsonify, render_template_string, request
import os
from PIL import Image   # for resolution

app = Flask(__name__)

FOLDERS = ['rejected', 'wallpapers']

GALLERY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Image Gallery</title>
  <style>
  body {
    font-family: 'Segoe UI', sans-serif;
    background: #f2f2f2;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  h1 {
    margin: 20px 0;
    color: #333;
  }
  .folder-tabs {
    margin: 10px 0;
  }
  .folder-tabs a {
    margin-right: 10px;
    padding: 6px 12px;
    text-decoration: none;
    color: white;
    border-radius: 5px;
    font-weight: bold;
  }
  .folder-tabs a.active {
    background-color: #007bff;
  }
  .folder-tabs a.inactive {
    background-color: #555;
  }
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 15px;
    width: 90%;
    max-width: 1200px;
    padding: 20px;
  }
  .image-card {
    position: relative;
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s ease-in-out;
    cursor: pointer;
  }
  .image-card:hover {
    transform: scale(1.03);
  }
  .image-card img {
    width: 100%;
    height: auto;
    display: block;
  }
  .image-card .info {
    padding: 8px;
    font-size: 13px;
    text-align: center;
    background: #fafafa;
    border-top: 1px solid #eee;
    color: #555;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .filename {
    word-break: break-all;
  }
  .dimension-tag {
    display: inline-block;
    background: #007bff;
    color: white;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    margin: auto;
    width: fit-content;
  }
  .delete-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(220, 53, 69, 0.85);
    color: white;
    border: none;
    padding: 5px 8px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
  }
  .delete-btn:hover {
    background: rgba(200, 35, 51, 0.95);
  }

  /* Floating filter input */
  #filter-bar {
    position: fixed;
    top: -60px; /* hidden initially */
    right: 20px;
    background: white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    padding: 10px 15px;
    border-radius: 8px;
    transition: top 0.3s ease-in-out;
    z-index: 10000;
  }
  #filter-input {
    width: 200px;
    padding: 6px 10px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 6px;
    outline: none;
  }

  /* Image Preview Modal */
  .modal {
    display: none;
    position: fixed;
    z-index: 9998;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.85);
    justify-content: center;
    align-items: center;
  }
  .modal img {
    max-width: 90%;
    max-height: 90%;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }

  /* Delete Confirmation Modal */
  .confirm-modal {
    display: none;
    position: fixed;
    z-index: 9999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.6);
    justify-content: center;
    align-items: center;
  }
  .confirm-box {
    background: white;
    padding: 20px 30px;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    text-align: center;
    max-width: 300px;
    animation: fadeIn 0.2s ease-in-out;
  }
  .confirm-box h3 {
    margin: 0 0 10px;
    color: #d9534f;
  }
  .confirm-box p {
    margin: 0 0 20px;
    color: #555;
  }
  .confirm-buttons {
    display: flex;
    justify-content: space-between;
  }
  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
  }
  .btn-cancel {
    background: #ccc;
    color: #333;
  }
  .btn-cancel:hover {
    background: #bbb;
  }
  .btn-delete {
    background: #d9534f;
    color: white;
  }
  .btn-delete:hover {
    background: #c9302c;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
  }
  </style>
  <script>
    let deleteTarget = null;
    let imageList = [];   // all filenames
    let currentIndex = -1; // index of previewed image

    // initialize list of images from template
    window.addEventListener("DOMContentLoaded", () => {
      imageList = [...document.querySelectorAll(".image-card")].map(card => card.id.replace("card-", ""));
    });

    function deleteImage(filename) {
      deleteTarget = filename;
      document.getElementById("confirm-modal").style.display = "flex";
    }

    async function confirmDelete() {
      if (!deleteTarget) return;
      try {
        let response = await fetch(`/gallery/${deleteTarget}?folder={{ current_folder }}`, { method: "DELETE" });
        let result = await response.json();
        if (response.ok && result.success) {
          let card = document.getElementById("card-" + deleteTarget);
          if (card) card.remove();

          // remove from imageList
          let idx = imageList.indexOf(deleteTarget);
          if (idx !== -1) {
            imageList.splice(idx, 1);

            // if this was the currently opened image, adjust
            if (currentIndex === idx) {
              if (imageList.length === 0) {
                closeModal();
              } else {
                // show next if available, else previous
                currentIndex = Math.min(idx, imageList.length - 1);
                showImage(currentIndex);
              }
            } else if (currentIndex > idx) {
              currentIndex--; // shift left since array shrank
            }
          }

        } else {
          alert("❌ Failed: " + (result.message || "Unknown error"));
        }
      } catch (err) {
        alert("⚠️ Network error: " + err);
      }
      closeConfirm();
    }

    function closeConfirm() {
      document.getElementById("confirm-modal").style.display = "none";
      deleteTarget = null;
    }

    // Show image in modal by index
    function showImage(index) {
      let filename = imageList[index];
      if (!filename) return;
      let modal = document.getElementById("modal");
      let modalImg = document.getElementById("modal-img");
      modalImg.src = "/images/{{ current_folder }}/" + filename;
      modal.dataset.filename = filename;
      modal.style.display = "flex";
      currentIndex = index;
    }

    function openModal(src, filename) {
      let idx = imageList.indexOf(filename);
      if (idx === -1) return;
      showImage(idx);
    }

    function closeModal() {
      document.getElementById("modal").style.display = "none";
      currentIndex = -1;
    }

    // Keyboard shortcuts
    document.addEventListener("keydown", function(event) {
      let confirmVisible = document.getElementById("confirm-modal").style.display === "flex";
      let previewVisible = document.getElementById("modal").style.display === "flex";

      if (confirmVisible) {
        if (event.key === "Enter") {
          confirmDelete();
        } else if (event.key === "Escape") {
          closeConfirm();
        }
      } else if (previewVisible) {
        if (event.key === "Escape") {
          closeModal();
        } else if (event.key === "Delete") {
          let modal = document.getElementById("modal");
          let filename = modal.dataset.filename;
          if (filename) deleteImage(filename);
        } else if (event.key === "ArrowRight") {
          if (currentIndex < imageList.length - 1) {
            showImage(currentIndex + 1);
          }
        } else if (event.key === "ArrowLeft") {
          if (currentIndex > 0) {
            showImage(currentIndex - 1);
          }
        }
      }
    });

    // Show/hide filter bar on scroll direction
    let lastScrollY = window.scrollY;
    window.addEventListener("scroll", () => {
      let filterBar = document.getElementById("filter-bar");
      if (window.scrollY < lastScrollY) {
        // scrolling up
        filterBar.style.top = "10px";
      } else {
        // scrolling down
        filterBar.style.top = "-60px";
      }
      lastScrollY = window.scrollY;
    });

    // Filter images by filename
    document.addEventListener("DOMContentLoaded", () => {
      let filterInput = document.getElementById("filter-input");
      filterInput.addEventListener("input", () => {
        let term = filterInput.value.toLowerCase();
        document.querySelectorAll(".image-card").forEach(card => {
          let filename = card.querySelector(".filename").textContent.toLowerCase();
          card.style.display = filename.includes(term) ? "" : "none";
        });
      });
    });
  </script>
</head>
<body>
  <!-- Floating Filter Input -->
  <div id="filter-bar">
    <input type="text" id="filter-input" placeholder="🔍 Filter images...">
  </div>

  <h1>📷 Image Gallery</h1>

  <!-- Folder Tabs -->
  <div class="folder-tabs">
  {% for f in ['rejected', 'wallpapers'] %}
    <a href="/gallery?folder={{ f }}" class="{% if current_folder == f %}active{% else %}inactive{% endif %}">
    {{ f.capitalize() }}
    </a>
  {% endfor %}
  </div>

  <!-- Image Grid -->
  <div class="gallery">
  {% for image in images %}
  <div class="image-card" id="card-{{ image.filename }}">
    <img loading="lazy" src="/images/{{ current_folder }}/{{ image.filename }}" alt="{{ image.filename }}"
       onclick="openModal('/images/{{ current_folder }}/{{ image.filename }}', '{{ image.filename }}')">
    <button class="delete-btn" onclick="event.stopPropagation(); deleteImage('{{ image.filename }}')">✖</button>
    <div class="info">
    <div class="filename">{{ image.filename }}</div>
    <span class="dimension-tag">{{ image.width }}x{{ image.height }}</span>
    </div>
  </div>
  {% endfor %}
  </div>

  <!-- Image Preview Modal -->
  <div id="modal" class="modal" onclick="if(event.target === this) closeModal()">
  <img id="modal-img" src="">
  </div>

  <!-- Delete Confirmation Modal -->
  <div id="confirm-modal" class="confirm-modal">
  <div class="confirm-box">
    <h3>Delete Image?</h3>
    <p>This will permanently remove the file from disk.</p>
    <div class="confirm-buttons">
    <button class="btn btn-cancel" onclick="closeConfirm()">Cancel (Esc)</button>
    <button class="btn btn-delete" onclick="confirmDelete()">Delete (Enter)</button>
    </div>
  </div>
  </div>
</body>
</html>
"""

@app.route('/images/<folder>/<filename>')
def serve_image(folder, filename):
  if folder not in FOLDERS:
    return "Folder not found", 404
  return send_from_directory(folder, filename)

@app.route('/gallery', methods=['GET'])
def gallery():
  folder = request.args.get("folder", "rejected")
  if folder not in FOLDERS:
    folder = "rejected"
  try:
    files = os.listdir(folder)
    image_files = []
    for file in files:
      if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp')):
        path = os.path.join(folder, file)
        try:
          with Image.open(path) as img:
            w, h = img.size
          image_files.append({"filename": file, "width": w, "height": h})
        except Exception:
          image_files.append({"filename": file, "width": "?", "height": "?"})

    image_files.sort(key=lambda x: (x["width"] * x["height"] if isinstance(x["width"], int) else 0), reverse=True)

    if request.args.get("json"):
      return jsonify(image_files)
    return render_template_string(GALLERY_TEMPLATE, images=image_files, current_folder=folder)
  except Exception as e:
    return jsonify({'error': 'Could not list images', 'message': str(e)}), 500

@app.route('/gallery/<filename>', methods=['DELETE'])
def delete_image(filename):
  folder = request.args.get("folder", "rejected")
  if folder not in FOLDERS:
    folder = "rejected"

  file_path = os.path.join(folder, filename)
  if not os.path.exists(file_path):
    return jsonify({'error': 'File not found'}), 404
  try:
    os.remove(file_path)
    return jsonify({'success': True, 'message': f'File {filename} deleted'})
  except Exception as e:
    return jsonify({'error': 'Failed to delete file', 'message': str(e)}), 500

if __name__ == '__main__':
  for f in FOLDERS:
    os.makedirs(f, exist_ok=True)
  app.run(debug=True, port=3000)
