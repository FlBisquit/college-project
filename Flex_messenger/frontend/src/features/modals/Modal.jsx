import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { closeModal } from './modalsSlice';
import VerifyEmailModal from './VerifyEmailModal';
import ConfirmDeleteModal from './ConfirmDeleteModal';

const Modal = () => {
  const { isOpen, type, data } = useSelector((state) => state.modals);
  const dispatch = useDispatch();

  if (!isOpen) return null;

  const renderModalContent = () => {
    switch (type) {
      case 'verifyEmail':
        return <VerifyEmailModal {...data} onClose={() => dispatch(closeModal())} />;
      case 'confirmDeleteServer':
        return <ConfirmDeleteModal {...data} onClose={() => dispatch(closeModal())} />;
      default:
        return (
          <div>
            <h3>{type}</h3>
            <p>{JSON.stringify(data)}</p>
            <button onClick={() => dispatch(closeModal())}>Close</button>
          </div>
        );
    }
  };

  return (
    <div className="modal-overlay" onClick={() => dispatch(closeModal())}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {renderModalContent()}
      </div>
    </div>
  );
};

export default Modal;