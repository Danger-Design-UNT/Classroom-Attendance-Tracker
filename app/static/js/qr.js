// static/js/qr.js

let html5QrcodeScanner;

function onScanSuccess(decodedText, decodedResult) {
    console.log("QR Code scanned:", decodedText);

    // Stop the scanner immediately after successful scan
    if (html5QrcodeScanner) {
        html5QrcodeScanner.clear();
    }

    // Show result to user
    const resultDiv = document.getElementById("qr-result");
    resultDiv.innerHTML = `
        <p><strong>Scanned successfully!</strong></p>
        <p>Redirecting to attendance page...</p>
    `;

    // Auto redirect after a short delay (so user sees the message)
    setTimeout(() => {
        window.location.href = decodedText;
    }, 800);   // 800ms delay — feels smooth
}

function onScanError(errorMessage) {
    // Optional: you can ignore or log errors
    console.warn("QR scan error:", errorMessage);
}

// Initialize the scanner when page loads
document.addEventListener("DOMContentLoaded", function() {
    html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader", 
        { 
            fps: 10, 
            qrbox: 250,
            rememberLastUsedCamera: true
        }
    );

    html5QrcodeScanner.render(onScanSuccess, onScanError);
});