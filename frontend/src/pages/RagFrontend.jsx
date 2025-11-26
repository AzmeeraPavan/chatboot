import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";

const API_URL = "http://127.0.0.1:8000";

const RagFrontend = () => {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatRef = useRef(null);

  // Auto-scroll chat window
  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [chat]);

  const handleSend = async () => {
    if (!question.trim() || loading) return;

    const userMessage = { sender: "user", text: question };
    setChat((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question, engine: "hf" })
      });

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();
      const botMessage = { sender: "bot", text: data.answer || "No answer returned." };

      setChat((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setChat((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Error connecting to backend." }
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4 text-center">SID Chatbot</h1>

        <div
          ref={chatRef}
          className="w-full bg-white rounded-lg shadow p-4 mb-4 h-[400px] overflow-y-auto"
        >
          {chat.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`mb-3 flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-2 rounded-lg max-w-[70%] ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.text}
              </div>
            </motion.div>
          ))}

          {loading && (
            <div className="text-gray-500 text-sm">Thinking...</div>
          )}
        </div>

        <div className="w-full flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 border rounded-lg p-2"
            placeholder="Ask a question..."
            disabled={loading}
          />
          <button
            onClick={handleSend}
            className="bg-blue-500 text-white px-4 rounded-lg disabled:bg-blue-300"
            disabled={loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RagFrontend;
