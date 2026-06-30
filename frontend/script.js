const API_BASE_URL = "https://ragchatbot-production-d0ef.up.railway.app";

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

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Show user message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content" style="align-items: flex-end;">
            <div class="message-bubble">${text}</div>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    userInput.value = '';
    chatArea.scrollTop = chatArea.scrollHeight;

    // Call the Railway backend
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text }),
        });
        const data = await response.json();

        // Show bot response
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot';
        
        let citationHTML = "";
        if (data.source_url && data.last_updated) {
            citationHTML = `<div class="citation" style="font-size: 0.8em; color: #666; margin-top: 5px;">
                📎 Source: <a href="${data.source_url}" target="_blank">${data.source_url}</a><br>
                🕐 Last updated from sources: ${data.last_updated}
            </div>`;
        }

        botDiv.innerHTML = `
            <div class="bot-avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                <div class="bot-name">HDFC Assistant</div>
                <div class="message-bubble">
                    ${data.answer}
                    ${citationHTML}
                </div>
            </div>
        `;
        chatContainer.appendChild(botDiv);
    } catch (error) {
        // Show error message
        const errDiv = document.createElement('div');
        errDiv.className = 'message bot';
        errDiv.innerHTML = `
            <div class="bot-avatar"><i class="ph ph-robot"></i></div>
            <div class="message-content">
                <div class="bot-name">HDFC Assistant</div>
                <div class="message-bubble">Sorry, something went wrong connecting to the server. Please try again.</div>
            </div>
        `;
        chatContainer.appendChild(errDiv);
    }

    chatArea.scrollTop = chatArea.scrollHeight;
}
