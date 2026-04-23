import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { verifyEmail, resendCode } from '../../features/auth/authSlice';
import { getMe } from '../../features/profile/profileSlice';
import { closeModal } from './modalsSlice';
import './VerifyEmailModal.css';

function VerifyEmailModal({ userId, email, onClose }) {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [code, setCode] = useState(() => localStorage.getItem('verifyCode') || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(
    !userId || userId === 'None' ? 'Сессия истекла, пожалуйста, войдите в систему снова' : null
  );
  const [resendMessage, setResendMessage] = useState('');

  const handleCodeChange = (e) => {
    const value = e.target.value.replace(/\D/g, '');
    setCode(value);
    localStorage.setItem('verifyCode', value);
  };

  const handleResend = async () => {
    setResendMessage('');
    const result = await dispatch(resendCode(userId));
    if (!result.error) {
      setResendMessage(result.payload?.message);
    } else {
      setResendMessage(result.payload?.message || 'Ошибка отправки');
    }
  };

  const handleSubmit = async () => {
    if (error) return;

    if (code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }

    setIsLoading(true);
    setError(null);

    const result = await dispatch(verifyEmail({ user_id: userId, code }));

    setIsLoading(false);

    if (verifyEmail.fulfilled.match(result)) {
      localStorage.removeItem('verifyCode');
      await dispatch(getMe());
      dispatch(closeModal());
      navigate('/');
    } else {
      setError(result.payload?.message || result.payload?.detail || 'Неверный код');
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <button className="modal-close-btn" onClick={onClose}>×</button>
        <div className="modal-icon">✉</div>

        <h3 className="modal-title">Подтвердите email</h3>
        <p className="modal-subtitle">
          Мы отправили код на <span>{email}</span>
        </p>

        {error && <p className="modal-error">{error}</p>}

        <input
          className="modal-input"
          type="text"
          inputMode="numeric"
          maxLength={6}
          placeholder="_ _ _ _ _ _"
          value={code}
          onChange={handleCodeChange}
        />

        <button
          className="modal-btn"
          onClick={handleSubmit}
          disabled={isLoading || code.length !== 6 || !!error}
        >
          {isLoading ? 'Проверяем...' : 'Подтвердить'}
        </button>

        <button className="modal-btn-secondary" onClick={handleResend}>
          Отправить код повторно
        </button>

        {resendMessage && <p className="modal-message">{resendMessage}</p>}

        <p className="modal-hint">Не пришло письмо? Проверьте папку «Спам»</p>
      </div>
    </div>
  );
}

export default VerifyEmailModal;