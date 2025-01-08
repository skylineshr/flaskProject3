document.addEventListener('click', (event) => {
    if (event.target.classList.contains('delete-comment-btn')) {
        const commentId = event.target.dataset.commentId;
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        fetch(`/delete_comment/${commentId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Comment deleted successfully!');
                    document.getElementById(`comment-${commentId}`).remove();
                } else {
                    alert('Error deleting comment.');
                }
            });
    }
});

/**
 * ✅ 移除评论函数
 */
function removeCommentFromPage(commentId) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    if (commentElement) {
        commentElement.remove();
    } else {
        console.error('Comment not found in DOM');
    }
}

/**
 * ✅ 显示闪现消息
 */
function displayFlashMessage(message, category) {
    const flashMessageContainer = document.getElementById('flash-messages');
    flashMessageContainer.innerHTML = `<div style="color: ${category === 'danger' ? 'red' : 'green'};">
            ${message}
        </div>`;
    setTimeout(() => {
        flashMessageContainer.innerHTML = '';  // 3秒后自动消失
    }, 3000);
};

/**
 * ✅ 动态添加评论到页面
 */
function addCommentToPage(comment) {
    const commentList = document.getElementById('comments-list');
    const commentElement = document.createElement('div');
    commentElement.id = `comment-${comment.id}`;
    commentElement.classList.add('comment-box');
    commentElement.innerHTML = `
            <p><strong>Comment:</strong> ${comment.content}</p>
            <p>User: ${comment.user} | Time: ${comment.date_posted}</p>
            <button class="btn btn-danger delete-comment-btn" data-comment-id="${comment.id}">
                Delete Comment
            </button>
        `;
    commentList.prepend(commentElement);
}

/**
 * ✅ 动态移除评论 (修复后的版本)
 */
function removeCommentFromPage(commentId) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    if (commentElement) {
        commentElement.remove();  // ✅ 确保元素被移除
    } else {
        displayFlashMessage('Comment not found on the page.', 'danger');
    }
}
