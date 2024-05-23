document.addEventListener("DOMContentLoaded", function() {
  const messageInput = document.getElementById('message-input');
  const messagesContainer = document.querySelector('.messages');

  messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && messageInput.value.trim() !== '') {
      const newMessage = document.createElement('div');
      newMessage.classList.add('message');
      newMessage.innerHTML = `
        <img class="avatar" src="Screenshot (299).png" alt="Avatar">
        <div class="message-content">
          <div class="message-header">
            <span class="username">You</span>
            <span class="timestamp">${new Date().toLocaleString()}</span>
          </div>
          <div class="message-body">${messageInput.value}</div>
        </div>
      `;
      messagesContainer.appendChild(newMessage);
      messageInput.value = '';
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });
});
