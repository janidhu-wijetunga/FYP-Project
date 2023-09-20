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
            chrome.runtime.sendMessage({ respond: newVal });
            
        })
    }
});