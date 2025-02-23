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

    // Initialize lastMessageDate from the last date separator in the HTML (if any)
    const chatLog = document.getElementById('chat-log');
    const dateSeparators = chatLog.querySelectorAll('.date-separator');
    let lastMessageDate = dateSeparators.length > 0 
    ? dateSeparators[dateSeparators.length - 1].innerText.trim() 
    : "";

    // Listen for messages from the server.
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // Create a Date object from the timestamp and format time as hh:mm
        const timestampDate = new Date(data.timestamp);
        let hours = timestampDate.getHours();
        let minutes = timestampDate.getMinutes();
        if (minutes < 10) {
            minutes = '0' + minutes;
        }
        const formattedTime = `${hours}:${minutes}`;

        // Format the full date string as "D, d.m.Y" (e.g., "Sun, 23.02.2025")
        const formattedDate = timestampDate.toLocaleDateString(undefined, {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).replace(/\//g, '.'); // Replace any slashes with dots if needed

        // If the date changes from the last message, insert a date separator.
        if (lastMessageDate !== formattedDate) {
            const dateSeparator = document.createElement('div');
            dateSeparator.classList.add('date-separator');
            dateSeparator.innerText = formattedDate;
            chatLog.appendChild(dateSeparator);
            lastMessageDate = formattedDate;
        }

        // Create a new div for the message
        const newMessage = document.createElement('div');
        const messageType = (data.sender === currentUser) ? 'sent' : 'received';
        newMessage.classList.add('chat-message', messageType);

        // Build the new HTML structure:
        // Sender's name on top and then a flex container with message content and timestamp.
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

document.addEventListener('DOMContentLoaded', function() {
    // Scroll chat log to the bottom on page load
    const chatLog = document.getElementById('chat-log');
    if (chatLog) {
        chatLog.scrollTop = chatLog.scrollHeight;
    }
});
