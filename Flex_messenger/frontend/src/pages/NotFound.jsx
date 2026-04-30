import { useNavigate } from 'react-router-dom';
import logo from '../assets/images/logo.png';
import './NotFound.css';

function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="notfound-bg">
      <div className="notfound-content">
        <div className="notfound-logo">
          <img src={logo} alt="logo" />
          <span>Flex messenger</span>
        </div>

        <div className="notfound-code">404</div>
        <p className="notfound-text">Страница не найдена</p>

        <button className="notfound-btn" onClick={() => navigate('/')}>
          На главную
        </button>
      </div>
    </div>
  );
}

export default NotFound;