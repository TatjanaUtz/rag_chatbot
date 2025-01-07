// Initialize the chat when the DOM content is loaded
document.addEventListener('DOMContentLoaded', initializeChat);

// Function to set up the chat interface
function initializeChat() {
    document.title = config.title;
    document.getElementById('chat-header').innerText = config.header;
    const chatMessages = document.getElementById('chat-messages');
    addMessageToChat('Bot', config.welcomeMessage, chatMessages);
}

// Function to handle sending a message
function sendMessage() {
    const userInput = getUserInput();
    if (isValidInput(userInput)) {
        const chatMessages = document.getElementById('chat-messages');
        addMessageToChat('You', userInput, chatMessages);
        clearInputField();
        scrollToBottom(chatMessages);
        debounce(() => sendToBackend(userInput, chatMessages), 300)();
    }
}

// Function to get the user's input from the input field
function getUserInput() {
    return document.getElementById('user-input').value;
}

// Function to validate the user's input
function isValidInput(input) {
    return input.trim() !== '';
}

// Function to add a message to the chat
function addMessageToChat(sender, message, chatMessages) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;
    chatMessages.appendChild(messageElement);
}

// Function to clear the input field
function clearInputField() {
    const userInput = document.getElementById('user-input');
    userInput.value = '';
    userInput.focus(); // Set focus back to the input field
}

// Function to scroll the chat to the bottom
function scrollToBottom(chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to send the user's input to the backend
function sendToBackend(userInput, chatMessages) {
    fetch(config.backendUrl, getFetchOptions(userInput))
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => handleBackendResponse(data, chatMessages))
        .catch(error => handleError(error, chatMessages));
}

// Function to get the fetch options for the backend request
function getFetchOptions(userInput) {
    return {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userInput })
    };
}

// Function to handle the backend response
function handleBackendResponse(data, chatMessages) {
    console.info("UI got response from backend", data);
    addMessageToChat('Bot', data.answer, chatMessages);
    scrollToBottom(chatMessages);
}

// Function to handle errors during the backend request
function handleError(error, chatMessages) {
    console.error('Error:', error);
    addMessageToChat('Bot', 'Sorry, something went wrong. Please try again later.', chatMessages);
    scrollToBottom(chatMessages);
}

// Debounce function to limit the rate at which a function can fire
function debounce(func, delay) {
    let debounceTimer;
    return function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(this, arguments), delay);
    };
}
