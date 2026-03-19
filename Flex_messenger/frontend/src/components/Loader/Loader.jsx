import logo from '../../assets/images/logo.png';
import './Loader.css';

function Loader() {
  return (
    <div className="loader-bg">
      <div className="loader-content">
        <div className="loader-logo">
          <img src={logo} alt="logo" />
          <span>Flex messenger</span>
        </div>
        <div className="loader-dots">
          <span /><span /><span />
        </div>
      </div>
    </div>
  );
}

export default Loader;