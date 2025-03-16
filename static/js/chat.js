// Popup Chat Window
function toggleChat() {
    const modal = document.getElementById('chatModal');
    modal.style.display = (modal.style.display === 'none' || modal.style.display === '') ? 'block' : 'none';
}

// Append Message
function appendMessage(sender, message) {
    const chatBody = document.getElementById("chatBody");
    const messageDiv = document.createElement("div");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
        messageDiv.innerHTML = `
            <div class="message-bubble">${message}</div>
            <img src="static/image/User.jpg" alt="User">
        `;
    } else {
        messageDiv.classList.add("bot-message");
        messageDiv.innerHTML = `
            <img src="static/image/Bot.jpg" alt="Bot">
            <div class="message-text">${message}</div>
        `;
    }

    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight; // scroll to bottom
}

// Send message
function sendMessage() {
    const userInput = document.getElementById("userInput");
    const message = userInput.value.trim();
    if (message === "") return;

    // User message
    appendMessage("user", message);

    // backend
    fetch("/detectIntent", {
        method: "POST",
        body: JSON.stringify({ message }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        // Bot message
        appendMessage("bot", data.reply);
    })
    .catch(error => console.error("Error:", error));

    userInput.value = ""; // intialize input
}