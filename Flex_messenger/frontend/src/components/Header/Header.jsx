import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import logo from "../../assets/images/logo.png";
import "./Header.css";

const Header = () => {
  const { isAuthenticated, user } = useSelector((state) => state.auth);

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
              <Link to="/messenger" className="nav-link">Messages</Link>
              <div className="user-profile">
                <span className="user-name">{user?.username || "User"}</span>
                <button className="btn-logout">Exit</button>
              </div>
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