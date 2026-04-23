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
            <section className="hero-section hero-section-centered">
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
          </>
        )}
      </main>
    </div>
  );
}

export default Home;