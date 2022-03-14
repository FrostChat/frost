let users_container = document.getElementById('users-container');
let user_divs = [];

function render_users(users, home_page = false) {
    users.forEach(user_obj => {
        let col_div = document.createElement('div');
        if (home_page) {
            col_div.classList.add('col-lg-3', 'col-md-6', 'col-sm-12', 'col-xs-12');
        } else {
            col_div.classList.add('col-12');
        }
        col_div.classList.add('mb-3');
        col_div.style.height = "max-content";

        let card_div = document.createElement('div');
        card_div.classList.add('card');
        card_div.classList.add('chat-card');
        card_div.style.backgroundColor = "#272727";
        card_div.style.cursor = "pointer";
        card_div.id = "user-" + user_obj.id;

        try {
            if (user_obj.id == user.id) {
                card_div.style.border = "2px solid #d7b1ff73";
            }
        } catch {}

        let card_body = document.createElement('div');
        card_body.classList.add('card-body');
        card_body.classList.add('chat-card-flexbox')

        let chat_title = document.createElement('h5');
        chat_title.classList.add('chat-title');
        chat_title.classList.add('m-0');
        chat_title.classList.add('p-0');
        chat_title.innerText = user_obj.username;

        let chat_image = document.createElement('img');
        chat_image.classList.add('chat-image');
        chat_image.src = user_obj.avatar_url;

        let chat_notifications = document.createElement('div');
        chat_notifications.classList.add('chat-notifications');
        chat_notifications.innerText = "0";

        card_body.appendChild(chat_image);
        card_body.appendChild(chat_title);
        card_body.appendChild(chat_notifications);
        card_div.appendChild(card_body);
        col_div.appendChild(card_div);

        users_container.appendChild(col_div);
        user_divs.push({user: user_obj, card: card_div});

        card_div.addEventListener('click', function() {
            window.location.href = '/app/chat/' + user_obj.id;
        });

        if (!context_menus.includes(card_div)) {
            card_div.addEventListener("contextmenu", function(e) {
                open_user_contextmenu(e, user_obj);
            });
            context_menus.push(card_div);
        }
    });
}

function add_notification(user_id) {
    let user_div = user_divs.find(x => x.user.id == user_id);
    let chat_notifications = user_div.card.getElementsByClassName('chat-notifications')[0];

    current_notifications = parseInt(chat_notifications.innerText);
    num_notifications = current_notifications + 1;

    if (num_notifications >= 9) {
        chat_notifications.style.opacity = "1";
        chat_notifications.innerText = "9+";
    } else {
        chat_notifications.style.opacity = "1";
        chat_notifications.innerText = num_notifications;
    }
}

function get_notifications(user_id) {
    let user_div = user_divs.find(x => x.user.id == user_id);
    let chat_notifications = user_div.card.getElementsByClassName('chat-notifications')[0];

    return parseInt(chat_notifications.innerText);
}

function reset_notifications(user_id) {
    let user_div = user_divs.find(x => x.user.id == user_id);
    let chat_notifications = user_div.card.getElementsByClassName('chat-notifications')[0];

    chat_notifications.style.opacity = "0";
    chat_notifications.innerText = "0";
}

function reset_notifications_loop() {
    if (document.hasFocus()) {
        for (let i = 0; i < users.length; i++) {
            if (users[i].id == user.id) {
                reset_notifications(users[i].id);
            } else {
                let notifications = get_notifications(users[i].id);
                if (notifications <= 0) {
                    reset_notifications(users[i].id);
                }
            }
        }
    }
    setInterval(() => { reset_notifications_loop() }, 1500);
}