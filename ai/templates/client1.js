// Establish WebSocket connection
const ws = new WebSocket('ws://192.168.1.132:8000');

// Get location via HTML5 Geolocation API
navigator.geolocation.getCurrentPosition((position) => {
  const { latitude, longitude } = position.coords;
  const payload = JSON.stringify({ type: 'location', latitude, longitude });

  // Send location via WebSocket
  ws.send(payload);
});
