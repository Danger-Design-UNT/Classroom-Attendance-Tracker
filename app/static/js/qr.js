document.addEventListener("DOMContentLoaded", () => {

    function onScanSuccess(qrCodeMessage) {
        const output = document.getElementById('qr-result');
        output.innerText = "Scanned: " + qrCodeMessage;

        // Optional: redirect after successful scan
        // window.location.href = "/some_route?data=" + encodeURIComponent(qrCodeMessage);
    }

    function onScanError(error) {
        console.warn(error);
    }

    const html5QrCode = new Html5Qrcode("qr-reader");

    html5QrCode.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: 250
        },
        onScanSuccess,
        onScanError
    );
});
