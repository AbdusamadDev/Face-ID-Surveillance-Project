// Create a new WebSocket.
const socket = new WebSocket('ws://192.168.1.132:8000');

// Connection opened
socket.addEventListener('open', (event) => {
    console.log('Connected to the WebSocket');
});

// Listen for messages
socket.addEventListener('message', (event) => {
    console.log('Received data:', event.data);

    // Try to parse it as JSON
    try {
        const jsonData = JSON.parse(event.data);
        console.log('Parsed data:', jsonData);
    } catch (error) {
        console.log('Data received is not JSON:', event.data);
    }
});

// Connection closed
socket.addEventListener('close', (event) => {
    console.log('WebSocket closed:', event);
});

// Errors
socket.addEventListener('error', (event) => {
    console.error('WebSocket Error:', event);
});
