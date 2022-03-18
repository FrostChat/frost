function send_message() {
    socket.emit('send_message', {
        content: message_box.value,
        receiver_id: user.id
    });
    message_box.value = '';
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
    let html;

    if (content.includes('http://') || content.includes('https://')) {
        let split_content = content.split(' ');
        let link_index = split_content.indexOf(split_content.find(x => x.includes('http://') || x.includes('https://')));
        let link = split_content[link_index];
        
        html = `<p style="margin: 0; padding: 0;">${split_content.slice(0, link_index).join(' ')} <a href="${link}" target="_blank">${link}</a> ${split_content.slice(link_index + 1).join(' ')}</p>`;

        if (link.endsWith('.gif') || link.endsWith('.png') || link.endsWith('.jpeg') || link.endsWith('.jpg')) {
            // let img_tag = '<img src="' + link + '" style="max-width: 100%;"></img>'
            let img_tag = `
            <div class="message-img">
                <img src="${link}" style="max-width: 100%;">
            </div>
            `;

            if (html == `<p style="margin: 0; padding: 0;"> <a href="${link}" target="_blank">${link}</a> </p>`) {
                html = img_tag;
            } else {
                html += '<br>' + img_tag;
            }
        }

    } else {
        html = "<p class='p-0 m-0'>" + content + "</p>";
    }

    return html;
}

let previous_day;
function add_message_div(message_obj) {
    if (message_obj.receiver_id == user.id || message_obj.author_id == user.id) {
        let outer_message_div = document.createElement('div');
        let message_div = document.createElement('div');
        let timestamp = document.createElement('p');
        let html_message = message_content_to_html(message_obj.content);

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
    if (e.keyCode == 13) {
        send_message();
    }
});