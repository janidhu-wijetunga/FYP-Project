let previousUrl = window.location.href;

function checkUrl() {
    const currentUrl = window.location.href;
    const youtubeUrlPattern = /^https:\/\/www\.youtube\.com\/watch\?v=/;

    if (currentUrl !== previousUrl && currentUrl.match(youtubeUrlPattern)) {
        chrome.runtime.sendMessage({ youtubeUrl: currentUrl });
        console.log("youtube url:", currentUrl);
        previousUrl = currentUrl;
    }
}

checkUrl();
setInterval(checkUrl, 1000);