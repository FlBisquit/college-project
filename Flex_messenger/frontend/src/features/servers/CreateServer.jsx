import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { createServer } from './serversSlice';
import Header from '../../components/Header/Header';
import './CreateServer.css';
import '../../pages/Home.css';

const CreateServer = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error } = useSelector(state => state.servers);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: true,
    avatar: null,
    max_users: ''
  });

  const [avatarPreview, setAvatarPreview] = useState(null);

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
    if (formData.max_users) {
      serverData.append('max_users', formData.max_users);
    }

    if (formData.avatar) {
      serverData.append('avatar', formData.avatar);
    }

    try {
      const result = await dispatch(createServer(serverData)).unwrap();
      navigate('/'); // Redirect to home after successful creation
    } catch (error) {
      console.error('Failed to create server:', error);
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <div className="home-bg">
      <Header />

      <div className="create-server-bg">
      <div className="create-server-container">
        <div className="create-server-header">
          <h1>Create Server</h1>
          <p>Give your server a personality with a name and an icon. You can always change it later.</p>
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
              <p>Upload an image to represent your server. Recommended size: 512x512px</p>
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
              <label htmlFor="max_users" style={{ fontSize: '14px', marginBottom: '4px' }}>Maximum users</label>
              <input
                type="number"
                id="max_users"
                name="max_users"
                value={formData.max_users}
                onChange={handleInputChange}
                min="1"
                max="12"
                style={{ width: '70px' }}
              />
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error.message || 'Failed to create server. Please try again.'}
            </div>
          )}

          <div className="form-actions">
            <button type="button" onClick={handleCancel} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isLoading || !formData.name.trim()} className="btn-primary">
              {isLoading ? 'Creating...' : 'Create Server'}
            </button>
          </div>
        </form>
      </div>
    </div>
    </div>
  );
};

export default CreateServer;