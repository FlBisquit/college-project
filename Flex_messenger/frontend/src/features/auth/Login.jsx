import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { login } from './authSlice';
import { useNavigate, Link } from 'react-router-dom';
import logo from '../../assets/images/logo.png';
import './Login.css';

function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoading, error } = useSelector((state) => state.auth);

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(login(formData));
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
        <h2>Sign Up</h2>
        <p className="auth-subtitle">Please fill your information below</p>

        {error && (
          <div className="auth-error">
            <p>Неверный логин или пароль</p>
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
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </span>
            <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
          </div>

          <div className="auth-actions">
            <button type="submit" disabled={isLoading} className="auth-btn-next">
              {isLoading ? 'Loading...' : 'Next'} <span className="btn-arrow">›</span>
            </button>
          </div>
        </form>

        <div className="auth-divider" />

        <p className="auth-switch">
          Don't have an account? <Link to="/register">Register to your account</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;