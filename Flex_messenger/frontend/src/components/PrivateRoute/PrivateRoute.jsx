import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Loader from '../Loader/Loader'

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useSelector((state) => state.auth);

  if (isLoading) return <Loader />;
  return isAuthenticated ? children : <Navigate to="/login" />;
}

export default PrivateRoute;