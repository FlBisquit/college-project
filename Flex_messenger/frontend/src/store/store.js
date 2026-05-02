import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import profileReducer from '../features/profile/profileSlice';
import serversReducer from '../features/servers/serversSlice';
import modalsReducer from '../features/modals/modalsSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    profile: profileReducer,
    servers: serversReducer,
    modals: modalsReducer,
  },
});