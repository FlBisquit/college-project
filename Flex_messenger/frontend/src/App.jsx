import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import Home from './pages/Home';
import Login from './features/auth/Login';
import Register from './features/auth/Register';
import Profile from './features/profile/Profile';
import CreateServer from './features/servers/CreateServer';
import EditServer from './features/servers/EditServer';
import PrivateRoute from './components/PrivateRoute/PrivateRoute';
import NotFound from './pages/NotFound';
import Modal from './features/modals/Modal';
import api from './api/axios';
import './styles/App.css';

function App() {
    useEffect(() => {
        // Получаем CSRF токен при первой загрузке
        api.get('csrf/');
    }, []);
  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/profile"
          element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          }
        />
        <Route
          path="/servers/create"
          element={
            <PrivateRoute>
              <CreateServer />
            </PrivateRoute>
          }
        />
        <Route
          path="/servers/:id/edit"
          element={
            <PrivateRoute>
              <EditServer />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Modal />
    </BrowserRouter>
  );
}

export default App;