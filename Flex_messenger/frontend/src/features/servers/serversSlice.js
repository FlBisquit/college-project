import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../api/axios';

// Получение списка серверов
export const fetchServers = createAsyncThunk(
  'servers/fetchServers',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await api.get('/servers/');
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Ошибка при загрузке');
    }
  }
);

// Создание нового сервера
export const createServer = createAsyncThunk(
  'servers/createServer',
  async (serverData, { rejectWithValue }) => {
    try {
      const { data } = await api.post('/servers/', serverData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Ошибка при создании');
    }
  }
);

// Обновление сервера
export const updateServer = createAsyncThunk(
  'servers/updateServer',
  async ({ id, serverData }, { rejectWithValue }) => {
    try {
      const { data } = await api.put(`/servers/${id}/`, serverData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Ошибка при обновлении');
    }
  }
);

// Удаление сервера
export const deleteServer = createAsyncThunk(
  'servers/deleteServer',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/servers/${id}/`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Ошибка при удалении');
    }
  }
);

const serversSlice = createSlice({
  name: 'servers',
  initialState: {
    servers: [],
    currentServer: null,
    isLoading: false,
    error: null,
  },
  reducers: {
    setCurrentServer: (state, action) => {
      state.currentServer = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Servers
      .addCase(fetchServers.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchServers.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        // Извлекаем массив из payload.data (согласно твоему логу)
        state.servers = Array.isArray(payload) ? payload : (payload.data || []);
      })
      .addCase(fetchServers.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Create Server
      .addCase(createServer.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(createServer.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        // Добавляем новый сервер в список (берем данные из payload.data или самого payload)
        const newServer = payload.data || payload;
        state.servers = [...(state.servers || []), newServer];
      })
      .addCase(createServer.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })

      // Update Server
      .addCase(updateServer.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(updateServer.fulfilled, (state, { payload }) => {
        state.isLoading = false;
        const updatedServer = payload.data || payload;
        state.servers = state.servers.map(server =>
          server.id === updatedServer.id ? updatedServer : server
        );
      })
      .addCase(updateServer.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })

      // Delete Server
      .addCase(deleteServer.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(deleteServer.fulfilled, (state, action) => {
        state.isLoading = false;
        state.servers = state.servers.filter(server => server.id !== action.payload);
      })
      .addCase(deleteServer.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { setCurrentServer, clearError } = serversSlice.actions;
export default serversSlice.reducer;