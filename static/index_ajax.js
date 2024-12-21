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

    function handleLikeDislike(event) {
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
                const questionCard = button.closest('.question-card');
                const likeCountDiv = questionCard.querySelector('.number');
                likeCountDiv.textContent = data.like_count;

                const likeButton = questionCard.querySelector('.like-button');
                const dislikeButton = questionCard.querySelector('.dislike-button');

                

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
        button.addEventListener('click', handleLikeDislike);
    });
});