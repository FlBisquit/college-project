import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import Header from "../components/Header/Header";
import "./Home.css";

function Home() {
  const { isAuthenticated } = useSelector((state) => state.auth);

  return (
    <div className="home-bg">
      <Header />

      <main className="home-content">
        {isAuthenticated ? (
              <div className="auth-bg">
                <div className="top-server-card">
                    <div className="server-body">
                      <h2>My servers</h2>
                      <button className='btn'>+</button>
                    </div>
                </div>
                <div className="main-server-card">
                    <div className="server-body">
                      <h2>Public servers</h2>
                    </div>
                </div>
              </div>
        ) : (
          <>
            <section className="hero-section">
              <div className="hero-info">
                <h1>Fast & Secure <br/><span>Communication</span></h1>
                <p>
                  Collaborate with your team and friends in real-time. 
                  Simple, powerful, and designed for privacy.
                </p>
                <div className="hero-btns">
                  <Link to="/register" className="btn-primary-large">Get Started for Free</Link>
                </div>
              </div>

              <div className="hero-mockup">
                <div className="chat-window">
                  <div className="chat-bubble">Hey! How is the project going? 🚀</div>
                  <div className="chat-bubble me">Almost done! Just polishing the UI.</div>
                  <div className="chat-bubble">Awesome, can't wait to see it.</div>
                </div>
              </div>
            </section>

            <section className="features-section">
              <div className="feature-item">
                <span className="feature-icon">⚡</span>
                <h3>Real-time</h3>
                <p>Instant messaging with low latency.</p>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🔒</span>
                <h3>Secure</h3>
                <p>Your data is protected and private.</p>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📱</span>
                <h3>Responsive</h3>
                <p>Perfect on any device or screen.</p>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default Home;