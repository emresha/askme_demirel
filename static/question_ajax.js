document.addEventListener('DOMContentLoaded', function() {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function handleQuestionLikeDislike(event) {
        event.preventDefault();

        const button = event.currentTarget;
        const postId = button.dataset.postId;
        const action = button.dataset.action;

        fetch("/toggle_question_like/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({
                'post_id': postId,
                'action': action,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                const likeCountDiv = document.querySelector(".question-number")
                likeCountDiv.textContent = data.like_count;

                const likeButton = document.querySelector('.like-button');
                const dislikeButton = document.querySelector('.dislike-button');

                if (data.like_value === 1) {
                    likeButton.classList.add('liked');
                } else {
                    likeButton.classList.remove('liked');
                }

                if (data.like_value === -1) {
                    dislikeButton.classList.add('liked');
                } else {
                    dislikeButton.classList.remove('liked');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function handleCommentLikeDislike(event) {
        event.preventDefault();

        const button = event.currentTarget;
        const commentId = button.dataset.commentId;
        const action = button.dataset.action;

        fetch("/toggle_comment_like/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({
                'comment_id': commentId,
                'action': action,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                const commentCard = button.closest('.answer');
                const likeCountDiv = commentCard.querySelector('.number');
                likeCountDiv.textContent = data.like_count;

                const likeButton = commentCard.querySelector('.comment-like-button');
                const dislikeButton = commentCard.querySelector('.comment-dislike-button');

                if (data.like_value === 1) {
                    likeButton.classList.add('liked');
                } else {
                    likeButton.classList.remove('liked');
                }

                if (data.like_value === -1) {
                    dislikeButton.classList.add('liked');
                } else {
                    dislikeButton.classList.remove('liked');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    document.querySelectorAll('.like-button, .dislike-button').forEach(function(button) {
        button.addEventListener('click', handleQuestionLikeDislike);
    });

    document.querySelectorAll('.comment-like-button, .comment-dislike-button').forEach(function(button) {
        button.addEventListener('click', handleCommentLikeDislike);
    });
});