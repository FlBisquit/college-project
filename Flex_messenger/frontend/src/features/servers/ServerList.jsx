import { useEffect, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchServers } from './serversSlice';
import { Pencil } from 'lucide-react';
import Loader from '../../components/Loader/Loader';
import './ServerList.css';

const ServerList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { servers, isLoading, error } = useSelector(state => state.servers);

  useEffect(() => {
    dispatch(fetchServers());
  }, [dispatch]);

  const { myServers, publicServers } = useMemo(() => {
    const data = Array.isArray(servers) ? servers : [];
    return {
      myServers: data.filter(s => s.is_owner === true),
      publicServers: data.filter(s => !s.is_owner)
    };
  }, [servers]);

  if (isLoading) return <Loader />;

  return (
    <div className="auth-bg">
      {/* Секция MY SERVERS */}
      <div className="server-card-container">
        <h2 className="section-title">My servers</h2>
        <div className="servers-grid">
          {myServers.map(server => (
            <div key={server.id} className="server-tile" onClick={() => navigate(`/servers/${server.id}`)}>
              <div className="tile-avatar-box">
                {server.avatar ? (
                  <img src={server.avatar} alt={server.name} />
                ) : (
                  <div className="tile-default-avatar">{server.name?.[0]?.toUpperCase()}</div>
                )}
                <span className="tile-label" style={{ color: '#86c331' }}>{server.owner?.username || 'you'}</span>
              </div>
              <button className="edit-server-btn" onClick={(e) => { e.stopPropagation(); navigate(`/servers/${server.id}/edit`); }}>
                <Pencil size={16} color="#1e1f22" />
              </button>
            </div>
          ))}
          {/* Заглушки до 6, кроме места для + */}
          {myServers.length < 5 && [...Array(5 - myServers.length)].map((_, i) => (
            <div key={`empty-my-${i}`} className="server-tile empty" />
          ))}
          {/* Кнопка ПЛЮС в конце */}
          <button className="add-server-btn" onClick={() => navigate('/servers/create')}>+</button>
        </div>
      </div>

      {/* Секция PUBLIC SERVERS */}
      <div className="server-card-container">
        <h2 className="section-title">Public servers</h2>
        <div className="servers-grid">
          {publicServers.map(server => (
            <div key={server.id} className="server-tile" onClick={() => navigate(`/servers/${server.id}/join`)}>
              <div className="tile-avatar-box">
                {server.avatar ? (
                  <img src={server.avatar} alt={server.name} />
                ) : (
                  <div className="tile-default-avatar">{server.name?.[0]?.toUpperCase()}</div>
                )}
                <span className="tile-label">{server.owner?.username || 'null'}</span>
              </div>
            </div>
          ))}
          {/* Заглушки до 18 */}
          {publicServers.length < 18 && [...Array(18 - publicServers.length)].map((_, i) => (
            <div key={`empty-public-${i}`} className="server-tile empty" />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ServerList;