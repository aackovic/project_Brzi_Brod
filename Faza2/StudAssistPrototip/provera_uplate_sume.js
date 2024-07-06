let amount = document.getElementById("amount");
let errorAmount = document.getElementById("errorAmount");

let contactForm = document.getElementById("form");

contactForm.addEventListener("submit", function (e) {
    let messageAmount = [];
    let amountInt = parseInt(amount.value); 

    if (amountInt > 16000 || amountInt <= 0) {
        messageAmount.push("* Neadekvatna vrednost");
    }

    if (messageAmount.length > 0) {
        e.preventDefault();
        errorAmount.innerText = messageAmount;
    } else {
        e.preventDefault();
        window.location.assign("uplata_sigurnosna_polja.html");
    }

});