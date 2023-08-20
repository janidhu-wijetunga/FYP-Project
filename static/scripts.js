document.getElementById('submitBtn').addEventListener('click', function() {
    const loadingPopup = document.getElementById('loadingPopup');
    const resultContainer = document.getElementsByClassName('result');

    // Show loading pop-up
    loadingPopup.style.display = 'block';
    resultContainer.style.display = 'none';

    // Simulate delay for demonstration
    setTimeout(function() {

        // Hide loading pop-up and show result container
        loadingPopup.style.display = 'none';
        resultContainer.style.display = 'block';
    }, 2000); // Simulate a delay of 2 seconds
});
