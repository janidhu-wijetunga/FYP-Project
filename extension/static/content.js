const currentUrl = window.location.href;
const youtubeUrlPattern = /^https:\/\/www\.youtube\.com\/watch\?v=/;

if (currentUrl.match(youtubeUrlPattern)) {

    chrome.runtime.sendMessage({youtubeUrl: currentUrl})
    console.log("youtube url:", currentUrl);
}