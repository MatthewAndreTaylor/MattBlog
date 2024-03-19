function toggleLike(postId) {
    var likeButton = document.getElementById("like-" + postId);
    var isLiked = likeButton.classList.contains("liked");
    var action = isLiked ? "unlike" : "like";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", `/like_action/${postId}/${action}`, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            likeButton.classList.toggle("liked");
            likeButton.textContent = isLiked ? "♥ like" : "♥ unlike";
        }
    };
    xhr.send();
}