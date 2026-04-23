import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { store } from './store/store';
import App from './App.jsx';
import { getMe } from './features/profile/profileSlice';
import './styles/index.css';

// Инициализируем auth state при загрузке
store.dispatch(getMe());

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </StrictMode>
);