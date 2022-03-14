function view_profile(user_id) {
    let user = users.find(x => x.id == user_id);

    if (user == undefined) {
        return;
    }

    let profile_viewer = new bootstrap.Modal(document.getElementById('profile-viewer'));
    let profile_viewer_avatar = document.getElementById('profile-viewer-avatar');
    let profile_viewer_title = document.getElementById('profile-viewer-title');
    let profile_viewer_biography = document.getElementById('profile-viewer-bio');
    let profile_viewer_bio_divider = document.getElementById('profile-viewer-bio-divider');

    profile_viewer_avatar.src = user.avatar_url;
    profile_viewer_title.innerText = user.username;

    if (user.bio != "") {
        profile_viewer_biography.innerText = user.bio.replaceAll("{newline}", "\n");
        profile_viewer_bio_divider.style.display = "block";
    } else {
        profile_viewer_bio_divider.style.display = "none";
        profile_viewer_biography.innerText = "";
    }

    profile_viewer.show();
}