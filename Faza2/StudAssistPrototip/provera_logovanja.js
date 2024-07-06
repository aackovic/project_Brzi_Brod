let username = document.getElementById("usernameForm");
let password = document.getElementById("passwordForm");
let errorUsername = document.getElementById("errorUsername");
let errorPassword = document.getElementById("errorPassword");

let contactForm = document.getElementById("form");

contactForm.addEventListener("submit", function (e) {
    let messageUsername = [];
    let messagePassword = [];

    let setUsername = new Set(["administrator", "moderator", "student"]);
    
    if (username.value === "" || username.value === null) {
        messageUsername.push("* Popunite polje");
    } else
    if (password.value === "" || password.value === null) {
        messagePassword.push("* Popunite polje");
    } else 
    if (setUsername.has(username.value) && password.value.length > 2) {
            e.preventDefault();
            window.location.assign(username.value + ".html");
    } else {
        messageUsername = [];
        errorUsername.innerText = "";
        messagePassword.push("* Neispravno korisničko ime/lozinka");
        errorPassword.innerText = messagePassword;
    }

    if (messageUsername.length > 0 || messagePassword.length > 0) {
        e.preventDefault();
        errorUsername.innerText = messageUsername;
        errorPassword.innerText = messagePassword;
    }

});