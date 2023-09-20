document.addEventListener('DOMContentLoaded', function () {
    const visitButton = document.getElementById('visit_website');
    const websiteURL = 'http://127.0.0.1:5000/';
    visitButton.addEventListener('click', function () {
        chrome.tabs.create({ url: websiteURL });
    });
});


document.getElementById("flaskValue").textContent = "Loading...";
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {

    document.getElementById("flaskValue").textContent = message.respond;
    updateFlaskValue();
})