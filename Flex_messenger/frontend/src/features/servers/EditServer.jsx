import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router-dom';
import { updateServer, fetchServers } from './serversSlice';
import { openModal } from '../modals/modalsSlice';
import Header from '../../components/Header/Header';
import './CreateServer.css';
import '../../pages/Home.css';

const EditServer = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { servers, myServers, isLoading, error } = useSelector(state => state.servers);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: true,
    avatar: null,
    max_members: 2
  });

  const [avatarPreview, setAvatarPreview] = useState(null);
  const [server, setServer] = useState(null);

  useEffect(() => {
    // Находим сервер по id
    const foundServer = [...servers, ...myServers].find(s => s.id === id);
    if (foundServer) {
      setServer(foundServer);
      setFormData({
        name: foundServer.name || '',
        description: foundServer.description || '',
        is_public: foundServer.is_public,
        avatar: null, // Не загружаем файл, только URL
        max_members: foundServer.max_members || 2
      });
      if (foundServer.avatar_url) {
        setAvatarPreview(foundServer.avatar_url);
      }
    } else {
      // Если сервер не найден в списке, можно загрузить отдельно, но пока предполагаем, что список загружен
      navigate('/');
    }
  }, [id, servers, navigate]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({ ...prev, avatar: file }));
      const reader = new FileReader();
      reader.onload = () => setAvatarPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const serverData = new FormData();
    serverData.append('name', formData.name);
    serverData.append('description', formData.description);
    serverData.append('is_public', formData.is_public);
    serverData.append('max_members', formData.max_members);

    if (formData.avatar) {
      serverData.append('avatar', formData.avatar);
    }

    try {
      await dispatch(updateServer({ id, serverData })).unwrap();
      navigate('/');
    } catch (error) {
      console.error('Failed to update server:', error);
    }
  };

  const handleDelete = () => {
    dispatch(openModal({
      type: 'confirmDeleteServer',
      data: { serverId: id, serverName: server?.name || 'Неизвестный сервер' }
    }));
  };

  return (
    <div className="home-bg">
      <Header />

      <div className="create-server-bg">
        <div className="create-server-container">
          <div className="create-server-header">
            <h1>Edit Server</h1>
            <p>Update your server's details and settings.</p>
          </div>

          <form onSubmit={handleSubmit} className="create-server-form">
            <div className="avatar-section">
              <div className="avatar-upload">
                <input
                  type="file"
                  id="avatar"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  style={{ display: 'none' }}
                />
                <label htmlFor="avatar" className="avatar-label">
                  {avatarPreview ? (
                    <img src={avatarPreview} alt="Server avatar" className="avatar-preview" />
                  ) : (
                    <div className="avatar-placeholder">
                      <span>+</span>
                    </div>
                  )}
                </label>
              </div>
              <div className="avatar-info">
                <h3>Server Icon</h3>
                <p>Upload a new image to change your server's icon. Recommended size: 512x512px</p>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="name">Server Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter server name"
                required
                maxLength={20}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Describe your server (optional)"
                rows={3}
              />
            </div>

            <div className="form-group" style={{ display: 'flex', alignItems: 'center' }}>
              <div>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_public"
                    checked={formData.is_public}
                    onChange={handleInputChange}
                  />
                  <span className="checkmark"></span>
                  Make this server public
                </label>
                <p className="checkbox-description">
                  Anyone can find and join this server. You can change this later.
                </p>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', marginLeft: 'auto' }}>
                <label htmlFor="max_members" style={{ fontSize: '14px', marginBottom: '4px' }}>Maximum users</label>
                <input
                  type="number"
                  id="max_members"
                  name="max_members"
                  value={formData.max_members}
                  onChange={handleInputChange}
                  min="1"
                  max="12"
                  style={{ width: '70px' }}
                />
              </div>
            </div>

            {error && (
              <div className="error-message">
                {typeof error === 'object' && error.avatar ? error.avatar[0] :
                 error.message || error.detail || 'Failed to update server. Please try again.'}
              </div>
            )}

            <div className="form-actions">
              <button type="submit" disabled={isLoading} className="btn-primary">
                {isLoading ? 'Updating...' : 'Update Server'}
              </button>
              <button type="button" onClick={handleDelete} className="btn-danger">
                Delete Server
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditServer;