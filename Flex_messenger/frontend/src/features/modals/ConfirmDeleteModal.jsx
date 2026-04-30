import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { deleteServer } from '../servers/serversSlice';
import { closeModal } from './modalsSlice';
import { Trash2 } from 'lucide-react';
import './ConfirmDeleteModal.css';

function ConfirmDeleteModal({ serverId, serverName, onClose }) {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading } = useSelector(state => state.servers);

  const handleDelete = async () => {
    try {
      await dispatch(deleteServer(serverId)).unwrap();
      navigate('/');
      dispatch(closeModal());
    } catch (error) {
      console.error('Failed to delete server:', error);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <button className="modal-close-btn" onClick={onClose}>×</button>
        <div className="modal-icon">
          <Trash2 size={40} color="#ffffff" />
        </div>

        <h3 className="modal-title">Удалить сервер</h3>
        <p className="modal-subtitle">
          Вы точно хотите удалить сервер? <br />
          <span>"{serverName}"</span> <br />
        </p>

        <button
          className="modal-btn"
          onClick={handleDelete}
          disabled={isLoading}
        >
          {isLoading ? 'Удаление...' : 'Удалить'}
        </button>
      </div>
    </div>
  );
}

export default ConfirmDeleteModal;