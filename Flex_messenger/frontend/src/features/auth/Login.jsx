import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { login } from './authSlice';
import logo from '../../assets/images/logo.png';
import '../../styles/Auth.css';

const EyeIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const EyeOffIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
    <line x1="1" y1="1" x2="23" y2="23"/>
  </svg>
);

function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(login(formData));
    if (!result.error) navigate('/');
  };

  return (
    <div className="auth-bg">
      <div className="auth-logo">
        <img src={logo} alt="logo" />
        <span>Flex messenger</span>
      </div>

      <div className="auth-card">
        <h2>Sign In</h2>
        <p className="auth-subtitle">Please fill your information below</p>

        {error && (
          <div className="auth-error">
            {typeof error === 'object'
              ? Object.entries(error).map(([field, messages]) => (
                  <p key={field}>{Array.isArray(messages) ? messages[0] : messages}</p>
                ))
              : <p>{error}</p>
            }
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="auth-form-row">
            <div className="auth-form-fields">
              <div className="auth-input-wrapper">
                <span className="auth-input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </span>
                <input type="text" name="username" placeholder="Login" value={formData.username} onChange={handleChange} required />
              </div>

              <div className="auth-input-wrapper">
                <span className="auth-input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="11" width="18" height="11" rx="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
                <span className="auth-input-toggle" onClick={() => setShowPassword(p => !p)}>
                  {showPassword ? <EyeOffIcon /> : <EyeIcon />}
                </span>
              </div>
            </div>

            <div className="auth-actions">
              <button type="submit" className={`auth-btn-next ${isLoading ? 'loading' : ''}`}>
                {'Next'} <span className="btn-arrow">›</span>
              </button>
            </div>
          </div>
        </form>

        <div className="auth-divider" />

        <p className="auth-switch">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;