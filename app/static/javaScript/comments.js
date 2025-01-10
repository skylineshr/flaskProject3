// static/javascript/comments.js
$(document).ready(function () {
    console.log("JavaScript successfully loaded - Comment Management with Timestamp");

    const csrfToken = $("#csrf_token").val();
    let currentPage = 1;
    const perPage = 5; // Number of comments per page

    /**
     * Display a floating toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of message ('success' or 'error')
     */
    function showToast(message, type = "success") {
        const toast = $(`<div class="toast-message ${type}">${message}</div>`);
        $("body").append(toast);
        setTimeout(() => {
            toast.fadeOut(500, function () {
                $(this).remove();
            });
        }, 1000); // Toast disappears after 1 second
    }

    /**
     * Load comments from the server with pagination and display them
     * @param {number} page - The page number to load
     */
    function loadComments(page = 1, pageName = "about") {
        $.ajax({
            url: `/api/comments/${pageName}?page=${page}&per_page=${perPage}`,
            type: "GET",
            success: function (response) {
                const commentsContainer = $("#comments-container");
                commentsContainer.empty();

                // Render comments and include a delete button for authorized users
                response.comments.forEach(comment => {
                    let deleteButton = '';
                    if (comment.is_admin || comment.user_id === response.current_user_id) {
                        deleteButton = `
                            <button class="btn btn-danger delete-comment" 
                                    data-id="${comment.id}">Delete</button>`;
                    }
                    commentsContainer.append(`
                        <div class="comment-item" data-id="${comment.id}">
                            <p><strong>${comment.username}</strong>: ${comment.content}</p>
                            <p><small>Time: ${comment.created_at}</small></p>
                            ${deleteButton}
                        </div>
                    `);
                });

                // Generate pagination buttons with current page highlighting
                $("#pagination-controls").empty();
                if (response.total_pages > 1) {
                    for (let i = 1; i <= response.total_pages; i++) {
                        const activeClass = (i === response.current_page) ? "active" : "";
                        $("#pagination-controls").append(`
                            <button class="btn btn-secondary pagination-btn ${activeClass}" data-page="${i}">
                                Page ${i}
                            </button>
                        `);
                    }
                }
            },
            error: function (xhr) {
                showToast("Failed to load comments. Check console for details.", "error");
            }
        });
    }

    /**
     * Submit a new comment using AJAX
     */
    $("#submit-comment").click(function () {
        const content = $("#new-comment").val().trim();
        if (!content) {
            showToast("Comment cannot be empty!", "error");
            return;
        }

        $.ajax({
            url: "/api/comments/about",
            type: "POST",
            contentType: "application/json",
            headers: { "X-CSRFToken": csrfToken },
            data: JSON.stringify({ content: content }),
            success: function (response) {
                showToast("Comment submitted successfully!", "success");
                $("#new-comment").val('');
                loadComments(currentPage);
            },
            error: function (xhr) {
                showToast("Failed to submit comment. Check console for details.", "error");
            }
        });
    });

    /**
     * Delete a comment using AJAX
     */
    $("#comments-container").on("click", ".delete-comment", function () {
        const commentId = $(this).data("id");

        $.ajax({
            url: `/api/comments/about`,
            type: "POST",
            contentType: "application/json",
            headers: { "X-CSRFToken": csrfToken },
            data: JSON.stringify({ comment_id: commentId }),
            success: function (response) {
                showToast("Comment deleted successfully!", "success");
                loadComments(currentPage);
            },
            error: function (xhr) {
                showToast("Failed to delete comment. Check console for details.", "error");
            }
        });
    });

    /**
     * Handle pagination button clicks
     */
    $("#pagination-controls").on("click", ".pagination-btn", function () {
        currentPage = $(this).data("page");
        loadComments(currentPage);
    });

    // Load the first page of comments when the page loads
    loadComments();
});
