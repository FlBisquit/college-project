import { useEffect, useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchServers } from './serversSlice';
import { Pencil } from 'lucide-react';
import Loader from '../../components/Loader/Loader';
import ServerTooltip from './ServerTooltip';
import './ServerList.css';
import './ServerTooltip.css';

const ServerList = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { servers, isLoading } = useSelector(state => state.servers);
  const { isAuthenticated } = useSelector(state => state.auth);

  const [showLoader, setShowLoader] = useState(true);
  const [hoveredServer, setHoveredServer] = useState(null);
  const [randomSeed] = useState(Math.random());

  // Массив дефолтных изображений
  const defaultImages = Array.from({length: 16}, (_, i) => `/assets/images/server_image${i + 1}.png`);

  // Функция для выбора дефолтной картинки на основе server.id
  const getDefaultImage = (serverId) => {
    // Преобразовать строку uuid в число
    const hash = serverId.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return defaultImages[hash % 16];
  };

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchServers());
    }
  }, [dispatch, isAuthenticated]);

  useEffect(() => {
    const timer = setTimeout(() => setShowLoader(false), 500);
    return () => clearTimeout(timer);
  }, []);



  const { myServers, publicServers } = useMemo(() => {
  const data = Array.isArray(servers) ? servers : [];

  const myServersList = [];
  const publicServersList = [];

  data.forEach(server => {
    if (server.is_owner || server.is_member) {
      myServersList.push(server);
    } else {
      publicServersList.push(server);
    }
  });

  return {
    myServers: myServersList,
    publicServers: publicServersList,
  };
}, [servers]);

  if (isLoading || showLoader) return <Loader />;

  return (
    <div className="auth-bg">
      {/* Секция MY SERVERS */}
      <div className="server-card-container">
        <h2 className="section-title">My servers</h2>
        <div className="servers-grid">
           {myServers.map(server => (
             <div
               key={server.id}
               className="server-tile"
               onClick={() => navigate(`/servers/${server.id}`)}
               onMouseEnter={() => setHoveredServer(server)}
               onMouseLeave={() => setHoveredServer(null)}
             >
               <div className="tile-avatar-box">
                 <img src={server.avatar_url || getDefaultImage(server.id)} alt={server.name} />
               </div>
              <button className="edit-server-btn" onClick={(e) => { e.stopPropagation(); navigate(`/servers/${server.id}/edit`); }}>
                <Pencil size={16} color="#1e1f22" />
              </button>
              {hoveredServer?.id === server.id && <ServerTooltip server={server} isMyServer />}
            </div>
          ))}
          {/* Заглушки до 6, кроме места для + */}
          {myServers.length < 5 && [...Array(5 - myServers.length)].map((_, i) => (
            <div key={`empty-my-${i}`} className="server-tile empty">
              <div className="tile-avatar-box">
                <img src={defaultImages[Math.floor((i + randomSeed * 16) % 16)]} alt="placeholder" />
              </div>
            </div>
          ))}
          {/* Кнопка ПЛЮС в конце */}
          <button className="add-server-btn" onClick={() => navigate('/servers/create')}>+</button>
        </div>
      </div>

      {/* Секция PUBLIC SERVERS */}
      <div className="server-card-container public-servers">
        <h2 className="section-title">Public servers</h2>
        <div className="servers-grid">
           {publicServers.map(server => (
             <div
               key={server.id}
               className="server-tile"
               onClick={() => navigate(`/servers/${server.id}`)}
               onMouseEnter={() => setHoveredServer(server)}
               onMouseLeave={() => setHoveredServer(null)}
             >
               <div className="tile-avatar-box">
                 <img src={server.avatar_url || getDefaultImage(server.id)} alt={server.name} />
               </div>
              {hoveredServer?.id === server.id && <ServerTooltip server={server} isMyServer={false} />}
            </div>
          ))}
          {/* Заглушки до 18 */}
          {publicServers.length < 18 && [...Array(18 - publicServers.length)].map((_, i) => (
            <div key={`empty-public-${i}`} className="server-tile empty">
              <div className="tile-avatar-box">
                <img src={defaultImages[Math.floor((i + randomSeed * 16) % 16)]} alt="placeholder" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ServerList;