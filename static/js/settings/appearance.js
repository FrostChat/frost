function change_theme(theme) {
    fetch("/api/user/@me/settings", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": self_user.api_key
        },
        body: JSON.stringify({
            theme: theme
        })
    }).then((response) => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert("Error updating theme");
        }
    })
}