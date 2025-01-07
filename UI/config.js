// Configuration object for the chatbot
const config = {
    // URL of the backend server to send user queries
    backendUrl: 'UI_BACKEND_URL' ?? 'http://localhost:8000/ask',

    // Title of the chatbot application
    title: 'UI_TITLE' ?? 'Test Chatbot',

    // Header text displayed at the top of the chat interface
    header: 'UI_HEADER' ?? 'Welcome to the test Chatbot',

    // Welcome message displayed when the chat is initialized
    welcomeMessage: 'UI_WELCOME_MESSAGE' ?? 'Hello! I am a test Chatbot. How can I help you?'
};
