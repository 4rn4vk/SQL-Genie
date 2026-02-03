import { useEffect, useRef, useState } from "react";
import "./styles.css";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/chat";

function Message({ sender, text }) {
  return (
    <div className={`bubble ${sender}`}>
      <span className="sender">{sender === "user" ? "You" : "SQL Genie"}</span>
      <p>{text}</p>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("connecting");
  const [streamingMessage, setStreamingMessage] = useState("");
  const streamingMessageRef = useRef("");
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");
    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("error");
    ws.onmessage = (event) => {
      if (event.data === "[[END_OF_MESSAGE]]") {
        const finalMsg = streamingMessageRef.current;
        if (finalMsg) {
          setMessages((prev) => [...prev, { sender: "assistant", text: finalMsg }]);
        }
        setStreamingMessage("");
        streamingMessageRef.current = "";
        return;
      }
      setStreamingMessage((prev) => {
        const next = prev + event.data;
        streamingMessageRef.current = next;
        return next;
      });
    };

    return () => ws.close();
  }, []);

  const sendMessage = () => {
    if (!input.trim()) return;
    const text = input.trim();
    setMessages((prev) => [...prev, { sender: "user", text }]);
    setInput("");

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(text);
    }
  };

  const onKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="page">
      <div className="panel">
        <header className="header">
          <div>
            <p className="eyebrow">SQL Genie</p>
            <h1>Ask your database</h1>
            <p className="sub">Natural language to SQL, streamed live.</p>
          </div>
          <span className={`status ${status}`}>{status}</span>
        </header>

        <main className="chat" role="log" aria-live="polite">
          {messages.map((msg, idx) => (
            <Message key={idx} sender={msg.sender} text={msg.text} />
          ))}
          {streamingMessage && (
            <Message sender="assistant" text={streamingMessage} />
          )}
        </main>

        <div className="composer">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="e.g., Who are the top 5 customers by spend this month?"
          />
          <button onClick={sendMessage} aria-label="Send">Send</button>
        </div>
      </div>
    </div>
  );
}
