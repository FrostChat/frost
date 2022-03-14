var start_chat_input = document.getElementById('start-chat-input');

start_chat_input.addEventListener('keyup', function(e) {
    if (e.keyCode == 13) {
        window.location.href = '/app/chat/' + start_chat_input.value;
    }
});