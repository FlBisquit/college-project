import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import logo from "../assets/images/logo.png";
import "./Home.css";

function Home() {
  const { isAuthenticated } = useSelector((state) => state.auth);

  return (
    <div className="home-bg">
      {isAuthenticated ? (
        <div style={{ textAlign: 'center', padding: '50px', color: '#fff' }}>
          <h1>Вы уже в системе</h1>
          <Link to="/messenger">Перейти в мессенджер</Link>
        </div>
      ) : (
        <>
          <div className="home-logo-center">
            <img src={logo} alt="logo" />
            <span>Flex messenger</span>
          </div>

          <section className="home-hero">
            <div className="home-text">
              <h1>Fast & Secure Messaging</h1>
              <p>Flex Messenger helps you chat with friends and teams instantly. Simple design, powerful features and real-time communication.</p>
              <div className="home-buttons">
                <Link to="/register" className="home-btn-primary">Get Started</Link>
                <Link to="/login" className="home-btn-secondary">Sign In</Link>
              </div>
            </div>

            <div className="chat-preview">
              <div className="chat-message">Hey! Are you coming today?</div>
              <div className="chat-message me">Yes! I'll be there in 10 minutes.</div>
              <div className="chat-message">Great! See you soon.</div>
            </div>
          </section>

          <section className="features">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real Time Chat</h3>
              <p>Messages are delivered instantly using modern web technologies.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Secure</h3>
              <p>Your communication stays private and protected.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Responsive</h3>
              <p>Works perfectly on desktop, tablet and mobile.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Beautiful UI</h3>
              <p>Clean interface designed for comfortable chatting.</p>
            </div>
          </section>

          <section className="cta">
            <h2>Start chatting today</h2>
            <p>Create your account and connect with friends instantly.</p>
            <Link to="/register"><button>Create Account</button></Link>
          </section>

          <footer className="footer">
            © 2026 Flex Messenger · <Link to="/login">Login</Link> · <Link to="/register">Register</Link>
          </footer>
        </>
      )}
    </div>
  );
}

export default Home;