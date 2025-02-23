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
        // Determine message type: 'sent' or 'received'
        const messageType = (data.sender === currentUser) ? 'sent' : 'received';
        newMessage.classList.add('chat-message', messageType);

        // Format timestamp as hh:mm
        const timestampDate = new Date(data.timestamp);
        let hours = timestampDate.getHours();
        let minutes = timestampDate.getMinutes();
        if (minutes < 10) {
            minutes = '0' + minutes;
        }
        const formattedTime = `${hours}:${minutes}`;

        // Build the new HTML structure:
        let htmlContent = `<strong class="sender">${data.sender}</strong>`;
        htmlContent += `<div class="message-body">`;
        htmlContent += `<div class="message-content">${data.message}`;
        if (data.image_url) {
            htmlContent += `<br><a href="${data.image_url}" target="_blank">
                                <img src="${data.image_url}" alt="Image from ${data.sender}" style="max-width: 200px;">
                            </a>`;
        }
        htmlContent += `</div>`;
        htmlContent += `<small class="timestamp">${formattedTime}</small>`;
        htmlContent += `</div>`;

        newMessage.innerHTML = htmlContent;
        chatLog.appendChild(newMessage);

        // Auto-scroll to the bottom of the chat log
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
