document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the room id and current user from data attributes
    const chatData = document.getElementById('chat-data');
    const roomId = chatData ? chatData.dataset.roomId : null;
    const currentUserElem = document.getElementById('current-user');
    const currentUser = currentUserElem ? currentUserElem.dataset.username : '';

    if (!roomId) {
        console.error('Room ID not found.');
        return;
    }

    const protocol = (window.location.protocol === "https:") ? "wss" : "ws";
    const chatSocket = new WebSocket(
        protocol + '://' + window.location.host + '/ws/' + roomId + '/'
    );

    // Listen for messages from the server.
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const chatLog = document.getElementById('chat-log');
        // Create a new div for the message
        const newMessage = document.createElement('div');
        // Determine message type
        const messageType = (data.sender === currentUser) ? 'sent' : 'received';
        newMessage.classList.add('chat-message', messageType);

        // Build message content
        let htmlContent = `<strong>${data.sender}:</strong><br>`;
        htmlContent += `${data.message}`;
        if (data.image_url) {
            htmlContent += `<br><a href="${data.image_url}" target="_blank">
                <img src="${data.image_url}" alt="Image from ${data.sender}" style="max-width: 200px;">
                </a>`;
        }
        // Convert timestamp to a readable format if needed
        // Here we simply output the raw ISO string. Adjust as needed.
        htmlContent += `<br><small>${data.timestamp}</small>`;
        newMessage.innerHTML = htmlContent;

        chatLog.appendChild(newMessage);

        // Auto-scroll: set scrollTop to the height of the container
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Socket closed unexpectedly');
    };

    const sendButton = document.getElementById('chat-message-send');
    const messageInput = document.getElementById('chat-message-input');
    const imageInput = document.getElementById('chat-image-input');

    sendButton.addEventListener('click', function() {
        const message = messageInput.value;
        const file = imageInput.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function() {
                const imageData = reader.result;
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'image': imageData
                }));
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

    messageInput.addEventListener('keyup', function(event) {
        if (event.keyCode === 13) {
            sendButton.click();
        }
    });
});
