import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "react-router-dom";
import api from "../api/axios";
import "./ChatRoom.css";

export default function ChatRoom() {
  const { roomName } = useParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("connecting");
  const socketRef = useRef(null);
  const logRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  // Load message history
  useEffect(() => {
    api.get(`chat/history/${roomName}/`)
      .then(res => {
        const history = res.data.map(msg => ({
          id: msg.id,
          kind: msg.image ? "image" : "text",
          author: msg.author_username,
          text: msg.text || "",
          imageUrl: msg.image || null,
          time: new Date(msg.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        }));
        setMessages(history);
      })
      .catch(() => {});
  }, [roomName]);

  // WebSocket setup
  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/ws/chat/${roomName}/`
    );
    socketRef.current = ws;

    ws.onopen = () => setStatus("open");
    ws.onclose = () => setStatus("closed");
    ws.onerror = () => setStatus("closed");

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);

      if (data.type === "text" || (!data.type && data.message)) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + Math.random(),
            kind: "text",
            author: data.author || "Unknown",
            text: data.message,
            time: data.created_at
              ? new Date(data.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : new Date().toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                }),
          },
        ]);
      }

      if (data.type === "image") {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + Math.random(),
            kind: "image",
            author: data.author || "Unknown",
            imageData: data.image_data,
            fileName: data.file_name,
            time: data.created_at
              ? new Date(data.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : new Date().toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                }),
          },
        ]);
      }

      if (data.type === "error") {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + Math.random(),
            kind: "system",
            text: `⚠ ${data.message}`,
          },
        ]);
      }

      if (data.type === "user_kicked") {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + Math.random(),
            kind: "system",
            text: `${data.username} был исключён из комнаты`,
          },
        ]);
      }
    };

    return () => ws.close();
  }, [roomName]);

  const sendMessage = useCallback(() => {
    const text = input.trim();
    if (!text || socketRef.current?.readyState !== WebSocket.OPEN) return;

    if (text.startsWith("/kick ")) {
      const username = text.slice(6).trim();
      socketRef.current.send(JSON.stringify({ type: "kick", username }));
      setInput("");
      return;
    }

    socketRef.current.send(JSON.stringify({ type: "text", message: text }));
    setInput("");
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file || socketRef.current?.readyState !== WebSocket.OPEN) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const base64 = evt.target.result.split(",")[1];
      socketRef.current.send(
        JSON.stringify({
          type: "image",
          image_data: base64,
          file_name: file.name,
        })
      );
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const statusColor =
    status === "open" ? "#3ecf8e" : status === "connecting" ? "#f59e0b" : "#f87171";
  const statusLabel =
    status === "open" ? "подключено" : status === "connecting" ? "подключение..." : "отключено";

  const avatarColors = ["#7c6af7", "#3ecf8e", "#f59e0b", "#38bdf8", "#fb7185", "#a3e635", "#f87171"];
  const colorFor = (name) => {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return avatarColors[Math.abs(hash) % avatarColors.length];
  };
  const initials = (name) => name.slice(0, 2).toUpperCase();

  return (
    <div className="cr-root">
      {/* Header */}
      <div className="cr-header">
        <span className="cr-header-hash">#</span>
        <span className="cr-header-title">{roomName}</span>
        <div className="cr-status-pill">
          <span className="cr-status-dot" style={{ background: statusColor }} />
          {statusLabel}
        </div>
      </div>

      <div className="cr-log" ref={logRef}>
        {messages.map((msg) => {
          if (msg.kind === "system") {
            return (
              <div className="cr-system" key={msg.id}>
                <span>{msg.text}</span>
              </div>
            );
          }
          const color = colorFor(msg.author);
          return (
            <div className="cr-msg" key={msg.id}>
              <div
                className="cr-avatar"
                style={{ background: `${color}22`, color }}
              >
                {initials(msg.author)}
              </div>
              <div className="cr-msg-body">
                <div className="cr-msg-meta">
                  <span className="cr-author" style={{ color }}>{msg.author}</span>
                  <span className="cr-time">{msg.time}</span>
                </div>
                {msg.kind === "text" && (
                  <div className="cr-text">{msg.text}</div>
                )}
                {msg.kind === "image" && (
                  <img
                    className="cr-img"
                    src={
                      msg.imageData
                        ? `data:image/png;base64,${msg.imageData}`
                        : msg.imageUrl
                    }
                    alt={msg.fileName || "image"}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="cr-input-area">
        <div className="cr-input-row">
          <label className="cr-icon-btn" title="Прикрепить изображение">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"
              stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
              <rect x="1" y="3" width="14" height="10" rx="2"/>
              <circle cx="5.5" cy="6.5" r="1.2"/>
              <path d="M1 10l3.5-3 3 3 2.5-2.5 4 4"/>
            </svg>
            <input
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleImageUpload}
              disabled={status !== "open"}
            />
          </label>

          <input
            className="cr-text-input"
            type="text"
            placeholder={`Сообщение в #${roomName}…`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={status !== "open"}
          />

          <button
            className="cr-send-btn"
            onClick={sendMessage}
            disabled={status !== "open" || !input.trim()}
          >
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none"
              stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1L1 5l4 1.5L6.5 11 12 1z"/>
            </svg>
          </button>
        </div>
        <div className="cr-hint">
          Enter — отправить &nbsp;·&nbsp; <code>/kick username</code> — исключить
        </div>
      </div>
    </div>
  );
}