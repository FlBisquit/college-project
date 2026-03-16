import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { register } from './authSlice';
import { useNavigate, Link } from 'react-router-dom';
import logo from '../../assets/images/logo.png';
import './Register.css';

function Register() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    date_birth: '',
    avatar: null,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, avatar: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(register(formData));
    if (!result.error) {
      navigate('/');
    }
  };

  return (
    <div className="auth-bg">
      <div className="auth-logo">
        <img src={logo} alt="logo" />
        <span>Flex messenger</span>
      </div>

      <div className="auth-card">
        <h2>Register</h2>
        <p className="auth-subtitle">Please fill your information below</p>

        {error && (
          <div className="auth-error">
            {typeof error === 'object'
              ? Object.entries(error).map(([field, messages]) => (
                  <p key={field}>{Array.isArray(messages) ? messages[0] : messages}</p>
                ))
              : error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="auth-input-wrapper">
            <span className="auth-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </span>
            <input type="text" name="username" placeholder="Login" value={formData.username} onChange={handleChange} required />
          </div>

          <div className="auth-input-wrapper">
            <span className="auth-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </span>
            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
          </div>

          <div className="auth-input-wrapper">
            <span className="auth-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
          </div>

          <div className="auth-input-wrapper">
            <span className="auth-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input type="password" name="password2" placeholder="Repeat password" value={formData.password2} onChange={handleChange} required />
          </div>

          <div className="auth-input-wrapper">
            <span className="auth-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
            </span>
            <input type="date" name="date_birth" value={formData.date_birth} onChange={handleChange} />
          </div>

          <div className="auth-actions">
            <button type="submit" disabled={isLoading} className="auth-btn-next">
              {isLoading ? 'Loading...' : 'Next'} <span className="btn-arrow">›</span>
            </button>
          </div>
        </form>

        <div className="auth-divider" />

        <p className="auth-switch">
          Already have an account? <Link to="/login">Login to your account</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;