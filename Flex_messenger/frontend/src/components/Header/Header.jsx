import { Link } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { getMe } from "../../features/profile/profileSlice";
import logo from "../../assets/images/logo.png";
import "./Header.css";

const Header = () => {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);
  const { user, isLoading } = useSelector((state) => state.profile);

  useEffect(() => {
    if (isAuthenticated && !user && !isLoading) {
      dispatch(getMe());
    }
  }, [isAuthenticated, user, isLoading, dispatch]);

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
              <Link to="/profile" className="btn-primary-sm">Profile</Link>
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