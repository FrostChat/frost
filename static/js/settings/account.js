let blocked_users_list = document.getElementById("blocked-users-list");
let blocked_users_col = document.getElementById("blocked-users-col");

function render_blocked_users() {
    blocked_users_list.innerHTML = "";
    for (let i = 0; i < blocked_users.length; i++) {
        let blocked_user = blocked_users[i];
        let blocked_user_element = document.createElement("li");
        let unblock_btn = document.createElement("button");

        unblock_btn.innerHTML = `<i class="fa-solid fa-xmark"></i>`;
        unblock_btn.classList.add("unblock-btn", "btn", "btn-danger");
        unblock_btn.setAttribute("onclick", `unblock_user("${blocked_user.id}")`);

        blocked_user_element.classList.add("list-group-item");
        blocked_user_element.innerText = `${blocked_user.username} (${blocked_user.id})`;
        blocked_user_element.id = `blocked-user-${blocked_user.id}`;
        blocked_user_element.appendChild(unblock_btn);
        
        blocked_users_list.appendChild(blocked_user_element);
    }
}

function unblock_user(user_id) {
    user_obj = users.find(x => x.id == user_id);

    fetch('/api/user/' + user_id + '/unblock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': self_user.api_key
        }
    }).then(response => {
        if (response.ok) {
            console.log("User unblocked");
            blocked_users = blocked_users.filter(x => x.id != user_id);
            try {
                let blocked_user_element = document.getElementById(`blocked-user-${user_id}`);
                blocked_user_element.parentNode.removeChild(blocked_user_element);
            } catch {}
        } else {
            alert("Error: " + response.statusText);
        }
    })
}

function check_blocked_users() {
    if (blocked_users.length > 0) {
        blocked_users_col.style.display = "block";
    } else {
        blocked_users_col.style.display = "none";
    }

    setInterval(check_blocked_users, 1000);
}