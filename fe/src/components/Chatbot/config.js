import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  initialMessages: [
    createChatBotMessage("Xin chào! Tôi là trợ lý ảo của hệ thống y tế. Tôi có thể giúp gì cho bạn?"),
  ],
  botName: "Health Assistant",
  customStyles: {
    botMessageBox: {
      backgroundColor: "#376B7E",
    },
    chatButton: {
      backgroundColor: "#376B7E",
    },
  },
};

export default config; 