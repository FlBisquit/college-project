import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';
import { openModal } from '../modals/modalsSlice';
import { getMe } from '../profile/profileSlice';

// Преобразует объект в FormData, пропуская пустые значения
const toFormData = (data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value);
    }
  });
  return formData;
};

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/users/auth/register/', toFormData(userData), {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data; // возвращаем весь ответ
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const verifyEmail = createAsyncThunk(
  'auth/verifyEmail',
  async ({ user_id, code }, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/users/auth/verify-email/', { user_id, code });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const resendCode = createAsyncThunk(
  'auth/resendCode',
  async (userId, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/users/auth/resend-code/', { user_id: userId });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue, dispatch }) => {
    try {
      const { data } = await api.post('/users/auth/login/', credentials);
      // Очищаем старый профиль и загружаем новый
      dispatch({ type: 'profile/clearProfile' });
      dispatch(getMe());
      return data.user;
    } catch (error) {
      const errorData = error.response?.data;
      if (errorData?.detail === "Email не подтверждён") {
        dispatch(openModal({
          type: 'verifyEmail',
          data: { userId: errorData.user_id, email: errorData.email }
        }));
        return rejectWithValue(null);
      }
      return rejectWithValue(errorData);
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { dispatch, rejectWithValue }) => {
    try {
      await api.post('/users/auth/logout/');
      // Очищаем профиль при выходе
      dispatch({ type: 'profile/clearProfile' });
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const handlePending = (state) => {
  state.isLoading = true;
  state.error = null;
};

const handleRejected = (state, action) => {
  state.isLoading = false;
  state.error = action.payload;
};

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    isAuthenticated: localStorage.getItem('isAuthenticated') === 'true',
    isLoading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // register
      .addCase(register.pending, handlePending)
      .addCase(register.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = payload;
      })
      .addCase(register.rejected, handleRejected)

      // verifyEmail
      .addCase(verifyEmail.pending, handlePending)
      .addCase(verifyEmail.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        localStorage.setItem('isAuthenticated', 'true');
      })
      // close modal on verify email success
      .addCase('modals/closeModal', () => {
        // navigate in component
      })
      .addCase(verifyEmail.rejected, handleRejected)

      // resendCode
      .addCase(resendCode.pending, handlePending)
      .addCase(resendCode.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(resendCode.rejected, handleRejected)

      // login
      .addCase(login.pending, handlePending)
      .addCase(login.fulfilled, (state) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        localStorage.setItem('isAuthenticated', 'true');
      })
      .addCase(login.rejected, handleRejected)

      // logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false;
        localStorage.removeItem('isAuthenticated');
      })

      // profile getMe
      .addCase('profile/getMe/fulfilled', (state) => {
        state.isAuthenticated = true;
        localStorage.setItem('isAuthenticated', 'true');
      })
      .addCase('profile/getMe/rejected', (state) => {
        state.isAuthenticated = false;
        localStorage.removeItem('isAuthenticated');
      })
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
