import { useState, useEffect } from "react";
import { apiService } from "../services/api_service";
import { ChatMessage } from "../lib/types";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await apiService.getChatHistory();
        setMessages(history);
      } catch (error) {
        console.error("Failed to load chat history:", error);
      }
    };
    fetchHistory();
  }, []);

  const sendMessage = async (content: string) => {
    const userMsg: ChatMessage = { role: "user", content };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const aiResponse = await apiService.sendChatMessage(content);
      setMessages(prev => [...prev, aiResponse]);
    } catch (error: any) {
      setMessages(prev => [...prev, { role: "system", content: "Error: " + error.message }]);
    } finally {
      setLoading(false);
    }
  };

  const clearMessages = async () => {
    try {
      await apiService.clearChatHistory();
      setMessages([]); 
    } catch (error) {
      console.error("Failed to clear chat:", error);
    }
  };

  return { messages, loading, sendMessage, clearMessages };
}