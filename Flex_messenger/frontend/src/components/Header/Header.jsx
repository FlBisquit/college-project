import './Header.css';
import { Search, Bell } from 'lucide-react';

function Header() {
    return (
        <header className="header">
            <div className="header-container">
                <div className="header-search">
                    <Search size={20} />
                    <input type="text" placeholder="Search..." />
                </div>
                
                <div className="header-actions">
                    <button className="header-icon-btn" title="Notifications">
                        <Bell size={20} />
                    </button>
                </div>
            </div>
        </header>
    );
}

export default Header;
