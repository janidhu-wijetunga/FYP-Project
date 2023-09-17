chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.youtubeUrl) {

        fetch('http://localhost:8080/receive_url', {
            method: 'POST',
            body: JSON.stringify({ url: message.youtubeUrl }),
            headers: {
                'Content-Type': 'application/json',
            }
        })
    }
});