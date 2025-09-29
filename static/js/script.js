// Dark mode toggle
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    if (currentTheme === 'dark') {
        body.classList.add('dark-mode');
    }

    darkModeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        const theme = body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    });

    // Progress bar simulation
    const progressBar = document.querySelector('.progress-bar');
    const progressFill = document.querySelector('.progress-fill');

    function updateProgress(percent) {
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
    }

    // Simulate progress during form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            if (progressBar) {
                progressBar.style.display = 'block';
                let progress = 0;
                const interval = setInterval(function() {
                    progress += 10;
                    updateProgress(progress);
                    if (progress >= 100) {
                        clearInterval(interval);
                    }
                }, 200);
            }
        });
    }

    // Quiz mode functionality
    const quizToggle = document.getElementById('quiz-toggle');
    if (quizToggle) {
        quizToggle.addEventListener('click', function() {
            body.classList.toggle('quiz-mode');
            this.textContent = body.classList.contains('quiz-mode') ? 'Exit Quiz' : 'Start Quiz';
        });
    }

    // Handle quiz answers
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('quiz-option')) {
            const questionDiv = e.target.closest('.quiz-question');
            const correctAnswer = questionDiv.dataset.correct;
            const allOptions = questionDiv.querySelectorAll('.quiz-option');

            allOptions.forEach(option => {
                option.disabled = true;
                if (option.textContent === correctAnswer) {
                    option.classList.add('correct');
                } else if (option === e.target) {
                    option.classList.add('incorrect');
                }
            });
        }
    });

    // Export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.dataset.format;
            const results = JSON.parse(this.dataset.results);
            if (format === 'json') {
                exportData('/export/json', results);
            } else if (format === 'pdf') {
                exportData('/export/pdf', results);
            }
        });
    });

    function exportData(url, data) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = url.includes('json') ? 'book_summary.json' : 'book_summary.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error:', error));
    }
});
