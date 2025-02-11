console.log("Digital Menu SaaS loaded.");
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.faq-question').forEach(button => {
        button.addEventListener('click', () => {
            const answer = button.nextElementSibling;
            const isActive = answer.classList.contains('active');

            // Close all other answers
            document.querySelectorAll('.faq-answer').forEach(ans => {
                ans.classList.remove('active');
            });
            document.querySelectorAll('.faq-question').forEach(btn => {
                btn.classList.remove('active');
            });

            // Toggle current answer
            if (!isActive) {
                answer.classList.add('active');
                button.classList.add('active');
            }
        });
    });
});