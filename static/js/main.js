window.addEventListener('load', function () {
    document.getElementById('loadingSpinner').style.display = 'none';
});
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('loadingSpinner').style.display = 'block';
});
// Dark Mode Toggle
document.getElementById('darkModeToggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});
