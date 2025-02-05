// static/chatbot.js
(function() {
    // 1) Read global config
    const config = window.myChatBotConfig || {};
    // The snippet includes something like:
    // window.myChatBotConfig = { apiKey: "...", chatbotId: "...", customerId: "...", design: {...} }
  
    // Required fields from config:
    const apiKey = config.apiKey;                      // Unique key for this chatbot
    const chatbotId = config.chatbotId;                // e.g. "123e4567-e89b-12d3-a456-426614174000"
    const customerId = config.customerId;              // e.g. "abc123"
  
    // Optional design fields:
    const design = config.design || {};
    const position = design.position || "bottom-right"; 
    const buttonColor = design.buttonColor || "#2c8ada";
  
    // 2) Create a floating chat button
    const chatButton = document.createElement("button");
    chatButton.innerText = "Chat with us";
    chatButton.style.position = "fixed";
    chatButton.style.bottom = "20px";
    chatButton.style.right = "20px";
    chatButton.style.backgroundColor = buttonColor;
    chatButton.style.color = "#fff";
    chatButton.style.padding = "12px 16px";
    chatButton.style.borderRadius = "5px";
    chatButton.style.cursor = "pointer";
    chatButton.style.zIndex = 999999;
  
    // If user wants bottom-left, adjust
    if (position === "bottom-left") {
      chatButton.style.left = "20px";
      chatButton.style.right = null;
    }
  
    document.body.appendChild(chatButton);
  
    // 3) On click, open the chat modal
    chatButton.addEventListener("click", function() {
      openChatPopup();
    });
  
    // We'll store a reference to the modal if already opened
    let chatModal = null;
  
    function openChatPopup() {
      if (chatModal) {
        // If already open, just show it
        chatModal.style.display = "block";
        return;
      }
  
      // Create a simple modal
      chatModal = document.createElement("div");
      chatModal.style.position = "fixed";
      chatModal.style.bottom = "80px";
      chatModal.style.right = "20px";
      chatModal.style.width = "300px";
      chatModal.style.height = "400px";
      chatModal.style.backgroundColor = "#fff";
      chatModal.style.border = "1px solid #ccc";
      chatModal.style.borderRadius = "8px";
      chatModal.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
      chatModal.style.zIndex = 999999;
  
      // Basic UI for messages
      chatModal.innerHTML = `
        <div style="background: #007bff; color: white; padding: 8px; text-align: center;">
          <strong>Chatbot</strong> 
          <span id="chatModalClose" style="float: right; cursor: pointer;">X</span>
        </div>
        <div id="chatModalMessages" style="flex: 1; overflow-y: auto; padding: 10px; height: 300px;"></div>
        <div style="display: flex; border-top: 1px solid #ccc;">
          <input id="chatModalInput" type="text" placeholder="Type your question..." 
            style="flex: 1; padding: 8px; border: none; outline: none;" />
          <button id="chatModalSend" style="padding: 8px; border: none; background: #007bff; color: #fff;">Send</button>
        </div>
      `;
  
      document.body.appendChild(chatModal);
  
      // Close button
      const closeBtn = document.getElementById("chatModalClose");
      closeBtn.addEventListener("click", () => {
        chatModal.style.display = "none";
      });
  
      // Send button & input
      const sendBtn = document.getElementById("chatModalSend");
      const inputField = document.getElementById("chatModalInput");
      const messagesDiv = document.getElementById("chatModalMessages");
  
      sendBtn.addEventListener("click", () => handleSend());
      inputField.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSend();
      });
  
      function handleSend() {
        const userQuestion = inputField.value.trim();
        if (!userQuestion) return;
        // Display user message
        addMessage("user", userQuestion);
        inputField.value = "";
  
        // 4) Call our LLM endpoint => POST /api/public/${chatbotId}/query
        fetch(`http://127.0.0.1:8000/api/public/${chatbotId}/query`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CHATBOT-API-KEY": apiKey  // The key we read from window.myChatBotConfig
          },
          body: JSON.stringify({ question: userQuestion })
        })
          .then(async (res) => {
            if (!res.ok) {
              let text = await res.text();
              throw new Error(`HTTP ${res.status} - ${text}`);
            }
            return res.json();
          })
          .then((data) => {
            // data might be { "answer": "LLM response", "sources": [...] }
            const answerText = data.answer || "No answer found.";
            addMessage("bot", answerText);
  
            // If you want to show sources:
            // if (data.sources) addMessage("system", "(Sources: " + data.sources.join(", ") + ")");
          })
          .catch((err) => {
            console.error("Error with chatbot query:", err);
            addMessage("bot", "Error: " + err.message);
          });
      }
  
      function addMessage(sender, text) {
        const msg = document.createElement("div");
        msg.style.margin = "5px 0";
        if (sender === "user") {
          msg.style.textAlign = "right";
        } else if (sender === "bot") {
          msg.style.textAlign = "left";
          msg.style.color = "blue";
        }
        msg.textContent = text;
        messagesDiv.appendChild(msg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      }
    }
  })();