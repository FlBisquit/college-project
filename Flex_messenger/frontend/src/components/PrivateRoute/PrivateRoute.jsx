import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Loader from '../Loader/Loader';

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading, user } = useSelector((state) => state.auth);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setReady(true));
    return () => clearTimeout(timer);
  }, []);

  if (!ready || isLoading) return <Loader />;

  // Проверяем аутентификацию и подтверждение email
  if (!isAuthenticated) return <Navigate to="/login" />;

  return children;
}

export default PrivateRoute;