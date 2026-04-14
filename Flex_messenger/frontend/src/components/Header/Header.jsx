import { Link } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { logout, getMe } from "../../features/auth/authSlice";
import logo from "../../assets/images/logo.png";
import "./Header.css";

const Header = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user, loading } = useSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated && !user && !loading) {
      dispatch(getMe());
    }
  }, [isAuthenticated, user, loading, dispatch]);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <header className="main-header">
      <div className="nav-container">
        <Link to="/" className="logo-section">
          <img src={logo} alt="Flex Logo" />
          <span>Flex messenger</span>
        </Link>

        <nav className="nav-actions">
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="nav-link">Profile</Link>
              <button className="btn-logout" onClick={handleLogout}>Exit</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Sign In</Link>
              <Link to="/register" className="btn-primary-sm">Get Started</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;