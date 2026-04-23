import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';

const handleError = (error) => {
  return error.response?.data || { message: 'Ошибка сети' };
};

const handlePending = (state) => {
  state.isLoading = true;
  state.error = null;
};

const handleRejected = (state, action) => {
  state.isLoading = false;
  state.error = action.payload;
};

const toFormData = (data) => {
  const formData = new FormData();
  Object.entries(data).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      formData.append(key, value);
    }
  });
  return formData;
};

export const getMe = createAsyncThunk(
  'profile/getMe',
  async (skipIfCached = false, { getState, rejectWithValue }) => {
    const { user } = getState().profile;
    if (user && !skipIfCached) return user;
    try {
      const { data } = await api.get('/users/profile/');
      return data;
    } catch (error) {
      return rejectWithValue(handleError(error));
    }
  }
);

export const updateProfile = createAsyncThunk(
  'profile/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const { data } = await api.patch('/users/profile/', toFormData(profileData));
      return data.user;
    } catch (error) {
      return rejectWithValue(handleError(error));
    }
  }
);

const profileSlice = createSlice({
  name: 'profile',
  initialState: {
    user: null,
    isLoading: false,
    initialized: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearProfile: (state) => {
      state.user = null;
      state.isLoading = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getMe.pending, handlePending)
      .addCase(getMe.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.user = payload;
        state.initialized = true;
      })
      .addCase(getMe.rejected, (state) => {
        state.isLoading = false;
        state.user = null;
        state.initialized = true;
      })

      .addCase(updateProfile.pending, handlePending)
      .addCase(updateProfile.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.user = payload;
      })
      .addCase(updateProfile.rejected, handleRejected);
  },
});

export const { clearError } = profileSlice.actions;
export default profileSlice.reducer;