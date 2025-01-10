document.addEventListener('DOMContentLoaded', () => {
    // 自动隐藏闪现消息
    setTimeout(function () {
        const flashMessages = document.getElementById('flash-messages');
        if (flashMessages) {
            flashMessages.style.transition = 'opacity 1s'; // 渐隐效果持续 1 秒
            flashMessages.style.opacity = 0;
            setTimeout(() => flashMessages.remove(), 1000); // 1 秒后完全移除
        }
    }, 1000); // 1000 毫秒 = 1 秒
});
