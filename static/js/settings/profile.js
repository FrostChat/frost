function update_avatar() {
    let avatar_input = document.getElementById('avatar-input');
    let api_key = self_user.api_key;
    let avatar_url = avatar_input.value;

    fetch("/api/user/@me", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": api_key
        },
        body: JSON.stringify({
            avatar_url: avatar_url
        })
    }).then((response) => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert("Error updating avatar");
        }
    })
}

function update_website() {
    let website_input = document.getElementById('website-input');
    let api_key = self_user.api_key;
    let website_url = website_input.value;

    fetch("/api/user/@me", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": api_key
        },
        body: JSON.stringify({
            website: website_url
        })
    }).then((response) => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert("Error updating avatar");
        }
    })
}

function update_bio() {
    let bio_textarea = document.getElementById('bio-textarea');
    let api_key = self_user.api_key;
    let bio = bio_textarea.value;

    fetch("/api/user/@me", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": api_key
        },
        body: JSON.stringify({
            bio: bio
        })
    }).then((response) => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert("Error updating avatar");
        }
    })
}