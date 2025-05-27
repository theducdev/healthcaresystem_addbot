class MessageParser {
  constructor(actionProvider) {
    this.actionProvider = actionProvider;
  }

  parse(message) {
    const lowerCaseMessage = message.toLowerCase();

    if (lowerCaseMessage.includes("xin chào") || 
        lowerCaseMessage.includes("hello") || 
        lowerCaseMessage.includes("hi")) {
      return this.actionProvider.handleGreeting();
    }

    if (lowerCaseMessage.includes("đặt lịch") || 
        lowerCaseMessage.includes("đặt khám") || 
        lowerCaseMessage.includes("lịch khám")) {
      return this.actionProvider.handleBooking();
    }

    return this.actionProvider.handleDefault();
  }
}

export default MessageParser; 