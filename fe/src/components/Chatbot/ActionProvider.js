class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }

  handleMessage = (message) => {
    fetch(`${process.env.REACT_APP_LLAMA_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        should_speak: true
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      const botMessage = this.createChatBotMessage(data.response);
      this.updateChatbotState(botMessage);
    })
    .catch(error => {
      console.error('Error:', error);
      const errorMessage = this.createChatBotMessage(
        "Xin lỗi, tôi đang gặp một chút vấn đề. Vui lòng thử lại sau."
      );
      this.updateChatbotState(errorMessage);
    });
  };

  handleDefault = () => {
    this.handleMessage("I need medical advice");
  };

  handleGreeting = () => {
    this.handleMessage("Hello, I need medical consultation");
  };

  handleBooking = () => {
    this.handleMessage("I want to book a medical appointment");
  };

  updateChatbotState(message) {
    this.setState((prevState) => ({
      ...prevState,
      messages: [...prevState.messages, message],
    }));
  }
}

export default ActionProvider; 