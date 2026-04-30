import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useSelector } from "react-redux";
import api from "../api/axios";
import Header from "../components/Header/Header";
import ImageModal from "../features/modals/ImageModal";
import "./ChatRoom.css";

const formatTime = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
};

const formatDateShort = (dateStr) => {
  const d = new Date(dateStr);
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
};

export default function ChatRoom() {
  const { roomName } = useParams();
  const [messages, setMessages] = useState([]);
  const [users, setUsers] = useState([]);
  const [input, setInput] = useState("");
  const [selectedImage, setSelectedImage] = useState(null);

  const { user } = useSelector((state) => state.profile);
  const currentUser = user?.username || localStorage.getItem("username") || "User";

  const socketRef = useRef(null);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  // Загрузка истории сообщений
  useEffect(() => {
    api.get(`chat/history/${roomName}/`).then(res => {
      const history = res.data.map(msg => ({
        id: msg.id,
        author: msg.author_username,
        text: msg.text || "",
        image: msg.image || null,
        time: formatTime(msg.created_at),
        date: formatDateShort(msg.created_at),
        avatar: msg.author_avatar || null,
      }));
      setMessages(history);
    });
  }, [roomName]);

  // WebSocket: обработка событий
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomName}/`);
    socketRef.current = ws;

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === "chat_message" || data.message) {
        const now = new Date();
        setMessages(prev => [...prev, {
          id: Date.now(),
          author: data.author,
          text: data.message,
          image: data.image_data ? `data:image/png;base64,${data.image_data}` : null,
          time: formatTime(now),
          date: formatDateShort(now),
          avatar: data.author_avatar || null,
        }]);
      }

      if (data.type === "image") {
        const now = new Date();
        setMessages(prev => [...prev, {
          id: Date.now(),
          author: data.author,
          text: "",
          image: data.image_data ? `data:image/png;base64,${data.image_data}` : null,
          time: formatTime(now),
          date: formatDateShort(now),
          avatar: data.author_avatar || null,
        }]);
      }

      if (data.type === "user_list") {
        setUsers(data.users);
      }

      if (data.type === "user_joined") {
        setUsers(prev => {
          if (prev.some(u => u.username === data.user.username)) return prev;
          return [...prev, data.user];
        });
      }

      if (data.type === "user_left") {
        setUsers(prev => prev.filter(u => u.username !== data.username));
      }
    };

    return () => ws.close();
  }, [roomName]);

  const sendMessage = () => {
    if (!input.trim()) return;
    socketRef.current.send(JSON.stringify({ type: "text", message: input }));
    setInput("");
  };

  const sendImage = (file) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1];
      socketRef.current.send(JSON.stringify({
        type: "image",
        image_data: base64,
        file_name: file.name
      }));
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      sendImage(file);
      e.target.value = null; // Reset input
    }
  };

  const openImageModal = (src) => {
    setSelectedImage(src);
  };

  const closeImageModal = () => {
    setSelectedImage(null);
  };

  const renderedItems = [];
  let lastDateLabel = null;
  messages.forEach((msg) => {
    if (msg.date !== lastDateLabel) {
      renderedItems.push({ type: "date", label: msg.date });
      lastDateLabel = msg.date;
    }
    renderedItems.push({ type: "msg", ...msg });
  });

  return (
    <>
      <Header />
      <div className="cr-root">
        <div className="cr-workspace">
          {/* SIDEBAR: Онлайн пользователи */}
          <div className="cr-sidebar">
            <div className="cr-sidebar-list">
              {users.map((user) => (
                <div key={user.username} className="cr-sidebar-card">
                  <div className="cr-sidebar-avatar">
                    <img src={user.avatar || '/assets/images/default_avatar.png'} alt={user.username} />
                  </div>
                  <div className="cr-sidebar-info">
                    <span className="cr-sidebar-name">{user.username}</span>
                    {user.is_owner && <span className="cr-crown">👑</span>}
                  </div>
                </div>
              ))}
            </div>
            <button className="cr-leave-btn" onClick={() => window.history.back()}>leave</button>
          </div>

          {/* CHAT WINDOW */}
          <div className="cr-chat-window">
            <div className="cr-log" ref={logRef}>
              {renderedItems.map((item, idx) => {
                if (item.type === "date") {
                  return (
                    <div className="cr-date-sticky" key={`date-${idx}`}>
                      <span className="cr-date-label">{item.label}</span>
                    </div>
                  );
                }

                const isMe = item.author === currentUser;
                return (
                  <div key={idx} className={`cr-item ${isMe ? "me" : "others"}`}>
                    <div className="cr-item-content">
                      <span className="cr-item-author">{isMe ? "you" : item.author}</span>
                      <div className="cr-item-bubble">
                        {item.image && <img src={item.image} alt="image" className="cr-item-image" onClick={() => openImageModal(item.image)} />}
                        {item.text && <span className="cr-item-text">{item.text}</span>}
                        <span className="cr-item-time">{item.time}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="cr-bottom-bar">
              <div className="cr-input-box">
                <input
                  className="cr-input"
                  placeholder="Write message here"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                />
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: "none" }}
                id="file-input"
              />
              <label htmlFor="file-input" className="cr-file-button">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
              </label>
              <button className="cr-send-button" onClick={sendMessage}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2">
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <ImageModal src={selectedImage} onClose={closeImageModal} />
    </>
  );
}
