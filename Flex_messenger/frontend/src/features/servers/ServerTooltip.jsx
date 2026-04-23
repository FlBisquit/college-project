import { Crown } from 'lucide-react';
import './ServerTooltip.css';

const ServerTooltip = ({ server, isMyServer }) => {
  const onlineCount = server.online_count || 0; // Настоящее количество онлайн из API
  const nameDisplay = server.name.length > 8 ? server.name.substring(0, 8) + '...' : server.name;
  const description = server.description ? (server.description.length > 10 ? server.description.substring(0, 10) + '...' : server.description) : 'No description';

  if (isMyServer) {
    return (
      <div className="server-tooltip">
        <div className="tooltip-item">
          <span className="tooltip-label">Online:</span>
          <span className="tooltip-value">{onlineCount}</span>
        </div>
        <div className="tooltip-item">
          <span className="tooltip-label">Name:</span>
          <span className="tooltip-value">{nameDisplay}</span>
        </div>
        <div className="tooltip-item">
          <span className="tooltip-label">Descrip:</span>
          <span className="tooltip-value">{description}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="server-tooltip">
      <div className="tooltip-item">
        <span className="tooltip-label">Online:</span>
        <span className="tooltip-value">{onlineCount}</span>
      </div>
      <div className="tooltip-item">
        <span className="tooltip-label">Name:</span>
        <span className="tooltip-value">{nameDisplay}</span>
      </div>
      <div className="tooltip-item">
        <Crown size={14} color="#FFD700" />
        <span className="tooltip-value">{server.owner?.username || 'Unknown'}</span>
      </div>
      <div className="tooltip-item">
        <span className="tooltip-label">Descrip:</span>
        <span className="tooltip-value">{description}</span>
      </div>
    </div>
  );
};

export default ServerTooltip;