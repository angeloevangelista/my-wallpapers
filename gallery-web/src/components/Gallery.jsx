import { useState, useEffect } from "react";
import { fetchImagesFromFolder } from "../api/github";
import ImageModal from "./ImageModal";

export default function Gallery({ folder }) {
  const [images, setImages] = useState([]);
  const [filter, setFilter] = useState("");
  const [modalImg, setModalImg] = useState(null);

  useEffect(() => {
    const load = async () => {
      const files = await fetchImagesFromFolder(folder);
      setImages(files);
    };
    load();
  }, [folder]);

  const filtered = images.filter(img => img.name.toLowerCase().includes(filter.toLowerCase()));

  return (
    <>
      <div className="filter-box">
        <input
          className="filter-input"
          placeholder="Search images..."
          value={filter}
          onChange={e=>setFilter(e.target.value)}
        />
      </div>

      <div className="gallery-grid">
        {filtered.map(file=>(
          <div key={file.sha} className="image-card" onClick={()=>setModalImg(file.download_url)}>
            <img src={file.download_url}/>
            <div className="filename">{file.name}</div>
          </div>
        ))}
      </div>

      <ImageModal src={modalImg} onClose={()=>setModalImg(null)}/>
    </>
  );
}