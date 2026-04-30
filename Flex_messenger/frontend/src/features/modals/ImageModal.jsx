import './ImageModal.css';

const ImageModal = ({ src, onClose }) => {
  if (!src) return null;

  return (
    <div className="cr-image-modal" onClick={onClose}>
      <div className="cr-image-modal-content">
        <img src={src} alt="large image" className="cr-modal-image" />
      </div>
    </div>
  );
};

export default ImageModal;