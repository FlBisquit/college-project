import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';

// Async thunks for chat
export const fetchMessages = createAsyncThunk(
  'chat/fetchMessages',
  async (channelId, { rejectWithValue }) => {
    try {
      const { data } = await api.get(`/chat/messages/?channel=${channelId}`);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ channelId, content }, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/chat/messages/', { channel: channelId, content });
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],          // Array of messages
    currentChannel: null,  // Current channel ID
    isLoading: false,
    error: null,
  },
  reducers: {
    setCurrentChannel: (state, action) => {
      state.currentChannel = action.payload;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMessages.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMessages.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.messages = payload;
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(sendMessage.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        state.messages.push(payload);
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { setCurrentChannel, addMessage, clearError } = chatSlice.actions;
export default chatSlice.reducer;