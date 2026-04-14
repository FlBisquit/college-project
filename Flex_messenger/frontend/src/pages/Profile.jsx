import { useEffect, useRef, useState, useMemo, memo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { getMe, logout, updateProfile } from '../features/auth/authSlice';
import Loader from '../components/Loader/Loader';
import Header from '../components/Header/Header';
import './Profile.css';

const BASE_URL = 'http://127.0.0.1:8000';

const getAvatarSrc = (user, preview) => {
  if (preview) return preview;
  if (!user.avatar) return `${BASE_URL}/static/images/default_avatar.png`;
  const url = user.avatar.startsWith('http') ? user.avatar : `${BASE_URL}${user.avatar}`;
  return url;
};

function Profile() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, loading } = useSelector((state) => state.auth);
  const fileInputRef = useRef(null);

  const [avatarPreview, setAvatarPreview] = useState(null);
  const [avatarFile, setAvatarFile] = useState(null);
  const [saveMessage, setSaveMessage] = useState('');
  const [formData, setFormData] = useState({ email: '', bio: '', date_birth: '' });

  const avatarSrc = useMemo(() => user ? getAvatarSrc(user, avatarPreview) : '', [user?.avatar, avatarPreview]);

  useEffect(() => {
    if (!user && !loading) {
      dispatch(getMe());
    }
    
    if (user) {
      setFormData({
        email: user.email || '',
        bio: user.bio || '',
        date_birth: user.date_birth || '',
      });
    }
  }, [dispatch, user, loading]);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleSave = () => {
    dispatch(updateProfile({
      ...formData,
      date_birth: formData.date_birth || null,
      ...(avatarFile && { avatar: avatarFile }),
    })).then((res) => {
      if (updateProfile.fulfilled.match(res)) {
        setAvatarPreview(null);
        setAvatarFile(null);
      }
    });
    setSaveMessage('Profile updated!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/login');
  };

  if (!user) return <Loader />;

  return (
    <div className="auth-bg">
      <Header />

      <div className="auth-card profile-card">
        <div className="profile-body">

          {/* Avatar */}
          <div className="profile-avatar-section">
            <div className="profile-avatar-wrapper" onClick={() => fileInputRef.current?.click()}>
              {avatarSrc ? (
                <img src={avatarSrc} alt="avatar" className="profile-avatar-img" />
              ) : (
                <div className="profile-avatar-placeholder">
                  {user.username?.[0]?.toUpperCase()}
                </div>
              )}
              <div className="profile-avatar-overlay">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit
              </div>
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handleAvatarChange} />
          </div>

          {/* Fields */}
          <div className="profile-fields">
            <div className="profile-field">
              <label className="profile-label">Login</label>
              <div className="auth-input-wrapper">
                <input type="text" value={user.username} disabled />
              </div>
            </div>

            <div className="profile-field">
              <label className="profile-label">Email</label>
              <div className="auth-input-wrapper">
                <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="your@email.com" />
              </div>
            </div>

            <div className="profile-field">
              <label className="profile-label">Bio</label>
              <textarea className="profile-bio" name="bio" value={formData.bio} onChange={handleChange} placeholder="Add a bio" rows={4} />
            </div>

            <div className="profile-field">
              <label className="profile-label">Date of Birth</label>
              <div className="auth-input-wrapper">
                <input type="date" name="date_birth" value={formData.date_birth} onChange={handleChange} />
              </div>
            </div>

            {saveMessage && <div className="save-message">{saveMessage}</div>}
          </div>
        </div>

        <div className="auth-divider" />

        <div className="profile-actions">
          <button onClick={handleLogout} className="btn-logout">Log out</button>
          <button onClick={handleSave} className="auth-btn-next">Save <span className="btn-arrow">›</span></button>
        </div>
      </div>
    </div>
  );
}

export default memo(Profile);