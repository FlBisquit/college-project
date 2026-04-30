import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { createServer, fetchMyServers } from './serversSlice';
import Header from '../../components/Header/Header';
import './CreateServer.css';
import '../../pages/Home.css';

const CreateServer = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { myServers, isLoading, error } = useSelector(state => state.servers);

  useEffect(() => {
    dispatch(fetchMyServers());
  }, [dispatch]);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: true,
    avatar: null,
    max_members: 2
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

  const handleCancel = () => navigate('/');

  const handleSubmit = async (e) => {
    e.preventDefault();

    let currentServers;
    try {
      currentServers = await dispatch(fetchMyServers()).unwrap();
    } catch (err) {
      console.error('Failed to fetch my servers:', err);
      return;
    }

    const handleSubmit = async (e) => {
      e.preventDefault();

      if (myServers.length >= 5) return;

      const data = new FormData();
      data.append('name', formData.name);
      data.append('description', formData.description);
      data.append('is_public', formData.is_public);
      data.append('max_members', formData.max_members);
      if (formData.avatar) {
        data.append('avatar', formData.avatar);
      }

      try {
        await dispatch(createServer(data)).unwrap();
        navigate('/');
      } catch (err) {
        console.error('Failed to create server:', err);
      }
    };

    if (myServers.length >= 5) return;

    const data = new FormData();
    data.append('name', formData.name);
    data.append('description', formData.description);
    data.append('is_public', formData.is_public);
    data.append('max_members', formData.max_members);
    if (formData.avatar) {
      data.append('avatar', formData.avatar);
    }
    
    try {
      await dispatch(createServer(data)).unwrap();
      navigate('/');
    } catch (err) {
      console.error('Failed to create server:', err);
    }
  };

  if (myServers && myServers.length >= 5) {
    return (
      <div className="home-bg">
        <Header />
        <div className="create-server-bg">
          <div className="create-server-container">
            <div className="create-server-header">
              <h1>Create Server</h1>
              <p>You have reached the maximum limit of 5 servers. You cannot create more servers.</p>
            </div>
            <div className="form-actions" style={{ justifyContent: 'center' }}>
              <button type="button" onClick={() => navigate('/')} className="btn-primary">
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

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