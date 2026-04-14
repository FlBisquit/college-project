import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';

const saveTokens = ({ access, refresh }) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

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
      const { data } = await api.post('/users/register/', toFormData(userData), {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      saveTokens(data.tokens);
      return data.user; // бэкенд должен вернуть user.id внутри user
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const verifyEmail = createAsyncThunk(
  'auth/verifyEmail',
  async ({ user_id, code }, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/users/verify-email/', { user_id, code });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/users/login/', credentials);
      saveTokens(data.tokens);
      return data.user;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const getMe = createAsyncThunk(
  'auth/getMe',
  async (_, { getState, rejectWithValue }) => {
    const { user } = getState().auth;
    if (user) return user;
    try {
      const { data } = await api.get('/users/profile/');
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      await api.post('/users/logout/', { refresh });
    } catch (error) {
      return rejectWithValue(error.response?.data);
    } finally {
      localStorage.clear();
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const { data } = await api.patch('/users/profile/', toFormData(profileData), {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return data.user;
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
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    isLoading: false,
    initialized: false,
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
      .addCase(verifyEmail.fulfilled, (state) => {
        state.isLoading = false;
        if (state.user) state.user.is_verified = true;
      })
      .addCase(verifyEmail.rejected, handleRejected)

      // login
      .addCase(login.pending, handlePending)
      .addCase(login.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = payload;
      })
      .addCase(login.rejected, handleRejected)

      // getMe
      .addCase(getMe.fulfilled, (state, { payload }) => {
        state.isAuthenticated = true;
        state.user = payload;
        state.initialized = true;
      })
      .addCase(getMe.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.initialized = true;
      })

      // logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
      })

      // updateProfile
      .addCase(updateProfile.pending, handlePending)
      .addCase(updateProfile.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.user = payload;
      })
      .addCase(updateProfile.rejected, handleRejected);
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;