export default function ImageModal({ src, onClose }) {
  if (!src) return null;
  return (
    <div className="modal-bg" onClick={onClose}>
      <img src={src} className="modal-img"/>
    </div>
  );
}