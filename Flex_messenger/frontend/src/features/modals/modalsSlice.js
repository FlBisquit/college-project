import { createSlice } from '@reduxjs/toolkit';

const loadModalState = () => {
  try {
    const saved = localStorage.getItem('modalState');
    const parsed = saved ? JSON.parse(saved) : { isOpen: false, type: null, data: null };

    // Don't restore verifyEmail modal on page reload
    if (parsed.type === 'verifyEmail') {
      return { isOpen: false, type: null, data: null };
    }

    return parsed;
  } catch {
    return { isOpen: false, type: null, data: null };
  }
};

const saveModalState = (state) => {
  try {
    localStorage.setItem('modalState', JSON.stringify(state));
  } catch {
    // Ignore
  }
};

const modalsSlice = createSlice({
  name: 'modals',
  initialState: loadModalState(),
  reducers: {
    openModal: (state, action) => {
      state.isOpen = true;
      state.type = action.payload.type;
      state.data = action.payload.data || null;
      saveModalState(state);
    },
    closeModal: (state) => {
      state.isOpen = false;
      state.type = null;
      state.data = null;
      saveModalState(state);
    },
  },
});

export const { openModal, closeModal } = modalsSlice.actions;
export default modalsSlice.reducer;