// demochatbot.js
class DemoChatbot {
  constructor({
    apiUrl,
    chatbotId,
    title = "Chatbot Demo",
    placeholder = "Type your question here...",
    theme = "light",
  }) {
    this.apiUrl = apiUrl;        // e.g. "/api/demo/query"
    this.chatbotId = chatbotId;  // The UUID of the chatbot (per-demo usage)
    this.title = title;
    this.placeholder = placeholder;
    this.theme = theme;
    this.init();
  }

  init() {
    this.createChatWindow();
    this.attachEventHandlers();
  }

  createChatWindow() {
    const chatbotContainer = document.createElement("div");
    chatbotContainer.id = "chatbot-container";
    chatbotContainer.innerHTML = `
      <div id="chatbot-header">${this.title}</div>
      <div id="chatbot-messages"></div>
      <div id="chatbot-input-container">
        <input id="chatbot-input" type="text" placeholder="${this.placeholder}" />
        <button id="chatbot-send">Send</button>
      </div>
    `;
    document.body.appendChild(chatbotContainer);

    // Apply theme by adding a class to the container
    chatbotContainer.classList.add(`chatbot-theme-${this.theme}`);
  }

  attachEventHandlers() {
    const sendButton = document.getElementById("chatbot-send");
    const inputField = document.getElementById("chatbot-input");

    sendButton.addEventListener("click", () => this.sendMessage(inputField.value));
    inputField.addEventListener("keypress", (e) => {
      if (e.key === "Enter") this.sendMessage(inputField.value);
    });
  }

  async sendMessage(message) {
    if (!message.trim()) return;

    const messagesContainer = document.getElementById("chatbot-messages");
    messagesContainer.innerHTML += `<div class="user-message">${message}</div>`;

    // Clear input
    const inputField = document.getElementById("chatbot-input");
    inputField.value = "";

    try {
      // If you store your JWT in localStorage or a cookie, retrieve it here
      const token = localStorage.getItem("access_token"); // Example

      // Send request to your DEMO endpoint, attaching the chatbotId
      const response = await fetch(this.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // If your backend checks Authorization for a logged-in user:
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ 
          chatbot_id: this.chatbotId,
          question: message,
        }),
      });

      const data = await response.json();
      console.log("Demo backend response:", data);

      // If your backend returns something like:
      // { "answer": "some text", "limit_reached": true/false }
      if (data.limit_reached) {
        messagesContainer.innerHTML += `<div class="bot-message">
          <strong>Demo limit reached!</strong><br/>
          ${data.answer}
        </div>`;
        // Optionally disable input for the user or show an alert
        return;
      }

      // Otherwise, display the demo answer
      const answer = data?.answer ?? "No answer found.";
      messagesContainer.innerHTML += `<div class="bot-message">${answer}</div>`;
      
    } catch (error) {
      console.error("Error sending demo message:", error);
      messagesContainer.innerHTML += `<div class="bot-message">Error: ${error.message}</div>`;
    }

    // Scroll to latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}