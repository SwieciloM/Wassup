// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the room id from the data attribute
    const chatData = document.getElementById('chat-data');
    const roomId = chatData ? chatData.dataset.roomId : null;
    if (!roomId) {
        console.error('Room ID not found.');
        return;
    }

    // Set up the WebSocket connection using the dynamic roomId
    const protocol = (window.location.protocol === "https:") ? "wss" : "ws";
    const chatSocket = new WebSocket(
        protocol + '://' + window.location.host + '/ws/' + roomId + '/'
    );

    // Listen for messages from the server.
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const chatLog = document.getElementById('chat-log');
        const newMessage = document.createElement('p');

        // If an image URL is included, display it.
        if (data.image_url) {
            newMessage.innerHTML = `<strong>${data.sender}:</strong> ${data.message} <br>
                <a href="${data.image_url}" target="_blank">
                    <img src="${data.image_url}" alt="Image from ${data.sender}" style="max-width: 200px;">
                </a>`;
        } else {
            newMessage.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
        }
        chatLog.appendChild(newMessage);
    };

    chatSocket.onclose = function(e) {
        console.error('Socket closed unexpectedly');
    };

    // Sending messages (with or without an image)
    const sendButton = document.getElementById('chat-message-send');
    const messageInput = document.getElementById('chat-message-input');
    const imageInput = document.getElementById('chat-image-input');

    sendButton.addEventListener('click', function() {
        const message = messageInput.value;
        const file = imageInput.files[0];

        // If a file is selected, convert it to a Base64 data URL.
        if (file) {
            const reader = new FileReader();
            reader.onload = function() {
                const imageData = reader.result; // Data URL string
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'image': imageData
                }));
                // Clear inputs after sending.
                messageInput.value = '';
                imageInput.value = '';
            };
            reader.readAsDataURL(file);
        } else {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        }
    });

    // Allow sending the message with the Enter key.
    messageInput.addEventListener('keyup', function(event) {
        if (event.keyCode === 13) {  // 13 is the Enter key
            sendButton.click();
        }
    });
});
