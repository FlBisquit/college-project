import { NavLink } from "react-router-dom";
import { Home, MessageSquare, User, LogOut } from "lucide-react";
import './Sidebar.css';

function Sidebar() {
  const handleLogout = () => {
    // TODO: реализовать выход
    console.log('Logout clicked');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-container">
        <div className="logo-section">
          <h3>Flex</h3>
        </div>
        
        <nav className="sidebar-nav">
          <ul>
            <li>
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                <Home size={20} />
                <span>Dashboard</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/chats" className={({ isActive }) => isActive ? 'active' : ''}>
                <MessageSquare size={20} />
                <span>Chats</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? 'active' : ''}>
                <User size={20} />
                <span>Profile</span>
              </NavLink>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
