import { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getMe, logout, updateProfile } from '../features/auth/authSlice';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

function Profile() {
  const BASE_URL = 'http://127.0.0.1:8000'
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const fileInputRef = useRef(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [nickname, setNickname] = useState('');
  const [bio, setBio] = useState('');
  const [avatarFile, setAvatarFile] = useState(null);


  useEffect(() => {
    if (!user) {
      dispatch(getMe());
    } else {
      setNickname(user.username || '');
      setBio(user.bio || '');
    }
  }, [dispatch, user]);

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/login');
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleSave = () => {
    dispatch(updateProfile({
      username: nickname,
      bio,
      ...(avatarFile && { avatar: avatarFile }),
    }));
  };

  if (!user) return <div className="profile-loading">Loading...</div>;

  const avatarSrc = avatarPreview || (user.avatar ? `${BASE_URL}${user.avatar}` : null);

  return (
    <div className="auth-bg">

      <div className="auth-card profile-card">

        <div className="profile-body">
          {/* Avatar */}
          <div className="profile-avatar-section">
            <div className="profile-avatar-wrapper" onClick={handleAvatarClick}>
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
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleAvatarChange}
            />
          </div>

          {/* Fields */}
          <div className="profile-fields">
            <div className="profile-field">
              <label className="profile-label">Login</label>
              <div className="auth-input-wrapper">
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="Your nickname"
                />
              </div>
            </div>

            <div className="profile-field">
              <label className="profile-label">Bio</label>
              <textarea
                className="profile-bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Add a bio"
                rows={4}
              />
            </div>
          </div>
        </div>

        <div className="auth-divider" />

        <div className="profile-actions">
          <button onClick={handleLogout} className="btn-logout">
            Log out
          </button>
          <button onClick={handleSave} className="auth-btn-next">
            Save <span className="btn-arrow">›</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Profile;