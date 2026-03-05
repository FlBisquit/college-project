import { Outlet } from "react-router-dom";
import Header from "../Header/Header";
import Sidebar from "../Sidebar/Sidebar";
import './Layout.css';

function Layout() {
    return (
        <div className="layout-container">
            <Sidebar />
            <div className="main-wrapper">
                <Header />
                <main className="content-area">
                    <div className="content-container">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
}

export default Layout;
