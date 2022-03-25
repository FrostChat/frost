function send_message() {
    if (message_box.value.length > 0) {
        socket.emit('send_message', {
            content: message_box.value,
            receiver_id: user.id
        });
        message_box.value = '';
        message_box.style.height = "28px";
    }
}

function delete_message(message, message_div_index) {
    socket.emit('delete_message', {
        message_id: message.id,
        message_div_index: message_div_index,
        receiver_id: message.receiver_id
    });
    close_contextmenu();
}

function message_content_to_html(content) {
    let html = marked.parse(content);
    return html.replaceAll("\n", "<br>");
}

let previous_day;
function add_message_div(message_obj, system = false) {
    if (message_obj.receiver_id == user.id || message_obj.author_id == user.id) {
        let outer_message_div = document.createElement('div');
        let message_div = document.createElement('div');
        let timestamp = document.createElement('p');
        let html_message = message_content_to_html(message_obj.content.replaceAll("{newline}", "\n"));

        date = new Date(message_obj.timestamp)

        timestamp.innerText = date.toLocaleTimeString();

        message_div.innerHTML = html_message;
        outer_message_div.classList.add("message");

        if (message_obj.author_id == self_user.id) {
            outer_message_div.classList.add("self");
            message_div.classList.add('self');
        }

        // if (message_obj.receiver_id == self_user.id) {
        //     timestamp.style.marginRight = '10px';
        //     outer_message_div.appendChild(timestamp);
        // }
        
        outer_message_div.appendChild(message_div);

        // if (message_obj.receiver_id != self_user.id) {
        //     timestamp.style.marginLeft = '10px';
        //     outer_message_div.appendChild(timestamp);
        // }

        message_container.appendChild(outer_message_div);
        message_divs.push(outer_message_div);
        message_container.scrollTop = message_container.scrollHeight;

        if (!context_menus.includes(outer_message_div)) {
            outer_message_div.addEventListener("contextmenu", function(e) {
                let index_of_message_div = message_divs.indexOf(outer_message_div);
                open_message_contextmenu(e, index_of_message_div);
            });
            context_menus.push(outer_message_div);
        }
    }
}

function render_messages(messages) {
    for (let i = 0; i < messages.length; i++) {
        add_message_div(messages[i]);
    }
}

message_box.addEventListener('keyup', function(e) {
    if (e.keyCode == 13 && !e.shiftKey) {
        send_message();
    }
});