import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  return (
    <div className="home-container">
      <h1>Добро пожаловать!</h1>
      
      {isAuthenticated ? (
        <div>
          <p>Привет, {user?.username}!</p>
          <Link to="/profile">
            <button className="btn-primary">Мой профиль</button>
          </Link>
        </div>
      ) : (
        <div className="auth-buttons">
          <Link to="/login">
            <button className="btn-primary">Войти</button>
          </Link>
          <Link to="/register">
            <button className="btn-secondary">Регистрация</button>
          </Link>
        </div>
      )}
    </div>
  );
}

export default Home;