const contextMenu = document.getElementById("context-menu");
const scope = document.querySelector("body");

const normalizePozition = (mouseX, mouseY) => {
    let {
        left: scopeOffsetX,
        top: scopeOffsetY,
    } = scope.getBoundingClientRect();

    scopeOffsetX = scopeOffsetX < 0 ? 0 : scopeOffsetX;
    scopeOffsetY = scopeOffsetY < 0 ? 0 : scopeOffsetY;

    const scopeX = mouseX - scopeOffsetX;
    const scopeY = mouseY - scopeOffsetY;

    const outOfBoundsOnX =
        scopeX + contextMenu.clientWidth > scope.clientWidth;

    const outOfBoundsOnY =
        scopeY + contextMenu.clientHeight > scope.clientHeight;

    let normalizedX = mouseX;
    let normalizedY = mouseY;

    if (outOfBoundsOnX) {
        normalizedX =
            scopeOffsetX + scope.clientWidth - contextMenu.clientWidth;
    }

    if (outOfBoundsOnY) {
        normalizedY =
            scopeOffsetY + scope.clientHeight - contextMenu.clientHeight;
    }

    return { normalizedX, normalizedY };
};

scope.addEventListener("click", (e) => {
    if (e.target.offsetParent != contextMenu) {
        close_contextmenu();
    }
});

function close_contextmenu() {
    contextMenu.classList.remove("visible");
    contextMenu.innerHTML = "";
}

function open_message_contextmenu(event, i) {
    msg = messages[i];
    event.preventDefault();

    const { clientX: mouseX, clientY: mouseY } = event;
    const { normalizedX, normalizedY } = normalizePozition(mouseX, mouseY);

    let delete_item_div = document.createElement('div');
    delete_item_div.classList.add('item');
    delete_item_div.innerText = 'Delete';
    delete_item_div.addEventListener('click', function () {
        delete_message(msg, i);
    });

    let copy_id_div = document.createElement('div');
    copy_id_div.classList.add('item');
    copy_id_div.innerText = 'Copy ID';
    copy_id_div.addEventListener('click', function () {
        navigator.clipboard.writeText(msg.id);
        close_contextmenu();
    });

    let copy_text_div = document.createElement('div');
    copy_text_div.classList.add('item');
    copy_text_div.innerText = 'Copy text';
    copy_text_div.addEventListener('click', function () {
        navigator.clipboard.writeText(msg.content);
        close_contextmenu();
    });

    contextMenu.classList.remove("visible");

    contextMenu.style.top = `${normalizedY}px`;
    contextMenu.style.left = `${normalizedX}px`;

    contextMenu.appendChild(copy_id_div);
    contextMenu.appendChild(copy_text_div);
    if (msg.author_id == self_user.id) { contextMenu.appendChild(delete_item_div); }

    setTimeout(() => {
        contextMenu.classList.add("visible");
    });
}

function open_user_contextmenu(event, user_obj) {
    event.preventDefault();

    const { clientX: mouseX, clientY: mouseY } = event;
    const { normalizedX, normalizedY } = normalizePozition(mouseX, mouseY);

    let mute_user_div = document.createElement('div');
    mute_user_div.classList.add('item');
    if (user_obj.is_muted) {
        mute_user_div.innerText = 'Unmute';
        mute_user_div.addEventListener('click', function () {
            unmute_user(user_obj.id);
            close_contextmenu();
        });
    } else {
        mute_user_div.innerText = 'Mute';
        mute_user_div.addEventListener('click', function () {
            mute_user(user_obj.id);
            close_contextmenu();
        });
    }

    let block_user_div = document.createElement('div');
    block_user_div.classList.add('item');
    if (user_obj.is_blocked) {
        block_user_div.innerText = 'Unblock';
        block_user_div.addEventListener('click', function () {
            unblock_user(user_obj.id);
            close_contextmenu();
        });
    } else {
        block_user_div.innerText = 'Block';
        block_user_div.addEventListener('click', function () {
            block_user(user_obj.id);
            close_contextmenu();
        });
    }

    let view_profile_div = document.createElement('div');
    view_profile_div.classList.add('item');
    view_profile_div.innerText = 'View profile';
    view_profile_div.addEventListener('click', function () {
        view_profile(user_obj.id);
        close_contextmenu();
    });

    let copy_id_div = document.createElement('div');
    copy_id_div.classList.add('item');
    copy_id_div.innerText = 'Copy ID';
    copy_id_div.addEventListener('click', function () {
        navigator.clipboard.writeText(user_obj.id);
        close_contextmenu();
    });

    let clear_notifications_div = document.createElement('div');
    clear_notifications_div.classList.add('item');
    clear_notifications_div.innerText = 'Mark as read';

    clear_notifications_div.addEventListener('click', () => {
        reset_notifications(user_obj.id);
        close_contextmenu();
    });

    contextMenu.classList.remove("visible");

    contextMenu.style.top = `${normalizedY}px`;
    contextMenu.style.left = `${normalizedX}px`;

    if (get_notifications(user_obj.id) > 0) { 
        contextMenu.appendChild(clear_notifications_div);
    }
    contextMenu.appendChild(mute_user_div);
    contextMenu.appendChild(block_user_div);
    contextMenu.appendChild(view_profile_div);
    contextMenu.appendChild(copy_id_div);

    setTimeout(() => {
        contextMenu.classList.add("visible");
    });    
}