console.log("I am background script!")
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    console.log("Received url:", message.youtubeUrl)
    if (message.youtubeUrl) {

        console.log("Received url:", message.youtubeUrl)

        fetch('http://localhost:8080/receive_url', {
            method: 'POST',
            body: JSON.stringify({ url: message.youtubeUrl }),
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => response.json())
        .then(data => {
            console.log(data.value);
            const newVal = data.value;

            notifications();
        })
    }
});

function notifications() {
                
    chrome.notifications.create(
        {
            title: "SpeechGuard",
            message: "Hate Speech Detected!",
            iconUrl: "../static/images/extensionLogo.png",
            type: "basic",
        }
    );

    chrome.notifications.onClicked.addListener(function () {
        const websiteURL = "http://127.0.0.1:5000/";
        chrome.tabs.create({ url: websiteURL });
    })
}