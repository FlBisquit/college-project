import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { verifyEmail } from '../../features/auth/authSlice';
import './VerifyEmailModal.css';

function VerifyEmailModal({ userId, email, onVerified }) {
  const dispatch = useDispatch();

  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }

    setIsLoading(true);
    setError(null);

    const result = await dispatch(verifyEmail({ user_id: userId, code }));

    setIsLoading(false);

    if (!result.error) {
      onVerified();
    } else {
      setError(result.payload?.detail || 'Неверный код');
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
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
          onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
        />

        <button
          className="modal-btn"
          onClick={handleSubmit}
          disabled={isLoading || code.length !== 6}
        >
          {isLoading ? 'Проверяем...' : 'Подтвердить'}
        </button>

        <p className="modal-hint">Не пришло письмо? Проверьте папку «Спам»</p>
      </div>
    </div>
  );
}

export default VerifyEmailModal;