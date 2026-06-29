const userInput = document.getElementById('userInput');
const chatContainer = document.getElementById('chatContainer');
const chatArea = document.getElementById('chatArea');

function fillInput(text) {
    userInput.value = text;
    userInput.focus();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Create user message element
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';

    // Simplified user message HTML
    messageDiv.innerHTML = `
        <div class="message-content" style="align-items: flex-end;">
            <div class="message-bubble">
                ${text}
            </div>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    
    // Clear input
    userInput.value = '';
    
    // Scroll to bottom
    chatArea.scrollTop = chatArea.scrollHeight;
}
