const socket = io("http://localhost:8080", { transports: ["websocket"] });

socket.emit('authenticate', { api_key: self_user.api_key });
socket.on('connected', () => { console.log('Connected to server') });
socket.on('disconnected', () => { console.log('Disconnected from server') });
socket.on('authenticated', () => { console.log('Authenticated') });

socket.on('message', function(data) {
    if (data.author_id == "system") {
        alert(data.error);
    } else {
        try {
            if (user.id != self_user.id) {
                messages.push(data);
                add_message_div(data);
    
                if (messages.length == 1) {
                    // check if user.id is not in users
                    let user_obj = users.find(x => x.id == user.id);
                    if (user_obj == undefined) {
                        location.reload()
                    }
                }
            }
        } catch {}
    
        if (!document.hasFocus() || data.author_id != user.id) {
            try {
                if (data.receiver_id != user.id && data.author_id != self_user.id) {
                    if (!user.is_muted) {
                        let audio = new Audio('/static/audio/notification.mp3');
                        audio.play();
                    }
                }
            } catch {}
            if (user.username == "duduser") {
                user = users.find(x => x.id == data.author_id);
            }
            if (!user.is_muted) {
                add_notification(data.author_id);
            }
        }
    }
});

socket.on('message_deleted', function(data) {
    try {
        if (user.id != self_user.id) {
            message_div = message_divs[data["message_div_index"]]
            message_container.removeChild(message_div);
            messages.splice(data["message_div_index"], 1);

            if (messages.length == 0) {
                // check if user.id is not in users
                let user_obj = users.find(x => x.id == user.id);
                if (user_obj != undefined) {
                    location.reload()
                }
            }
        }
    } catch {}
});