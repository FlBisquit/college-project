import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import Header from "../components/Header/Header";
import Loader from "../components/Loader/Loader";
import ServerList from "../features/servers/ServerList";
import "./Home.css";

function Home() {
  const { isAuthenticated } = useSelector((state) => state.auth);
  const { initialized } = useSelector((state) => state.profile);

  if (!initialized) {
    return <Loader />;
  }

  return (
    <div className="home-bg">
      <Header />

      <main className="home-content">

        {isAuthenticated ? (
          <ServerList />
        ) : (
          <>
            {/* Hero Section */}
            <section className="hero-section hero-section-centered">
              <div className="hero-info">
                <h1>Connect Instantly <br/><span>With Flex Messenger</span></h1>
                <p>
                  Experience lightning-fast messaging with end-to-end encryption.
                  Create servers, join communities, and chat with your team in real-time.
                </p>
                <div className="hero-btns">
                  <Link to="/register" className="btn-primary-large">Start Chatting Now</Link>
                  <Link to="/login" className="link-secondary">Already have an account?</Link>
                </div>
              </div>

              <div className="hero-mockup">
                <div className="mockup-header">
                  <div className="mockup-avatar"></div>
                  <div className="mockup-title">Team Project 💻</div>
                  <div className="mockup-status">3 members online</div>
                </div>
                <div className="chat-window">
                  <div className="chat-message">
                    <div className="message-avatar">A</div>
                    <div className="message-content">
                      <div className="message-author">Artem</div>
                      <div className="message-text">Just pushed the latest updates! 🚀</div>
                    </div>
                  </div>
                  <div className="chat-message me">
                    <div className="message-content">
                      <div className="message-text">Great work! Let me check it out.</div>
                    </div>
                  </div>
                  <div className="chat-message">
                    <div className="message-avatar">S</div>
                    <div className="message-content">
                      <div className="message-author">Maksim</div>
                      <div className="message-text">The UI looks amazing! 🔥</div>
                    </div>
                  </div>
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </section>

            {/* Features Section */}
            <section className="features-section">
              <div className="feature-item">
                <div className="feature-icon">⚡</div>
                <h3>Lightning Fast</h3>
                <p>Real-time messaging with instant delivery and read receipts.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🔒</div>
                <h3>Secure & Private</h3>
                <p>End-to-end encryption keeps your conversations safe and private.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">👥</div>
                <h3>Team Collaboration</h3>
                <p>Create servers and channels to organize your team communication.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">📱</div>
                <h3>Cross Platform</h3>
                <p>Access your messages from any device, anywhere, anytime.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🎨</div>
                <h3>Modern Design</h3>
                <p>Clean, intuitive interface designed for the best user experience.</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🌟</div>
                <h3>Free Forever</h3>
                <p>No hidden fees, no premium tiers. Completely free to use.</p>
              </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
              <div className="cta-content">
                <h2>Ready to get started?</h2>
                <p>Join thousands of users already using Flex Messenger for their communication needs.</p>
                <Link to="/register" className="btn-primary-large">Create Your Account</Link>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default Home;