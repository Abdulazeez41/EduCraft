// Dark Mode Toggle
function toggleTheme() {
  document.body.classList.toggle("dark-mode");
}

// Add dark mode styles dynamically
document.addEventListener("DOMContentLoaded", function () {
  let darkModeStyle = document.createElement("style");
  darkModeStyle.innerHTML = `
        .dark-mode {
            background-color: #212529;
            color: white;
        }
        .dark-mode .sidebar {
            background-color: #1d2124;
        }
        .dark-mode .card {
            background-color: #343a40;
            color: white;
        }
    `;
  document.head.appendChild(darkModeStyle);
});
