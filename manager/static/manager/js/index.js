document.addEventListener("DOMContentLoaded", function () {
    // Inicializa o leitor de QR Code após o DOM estar pronto
    const html5QrCode = new Html5Qrcode("reader");
    const qrCodeSuccessCallback = (decodedText, decodedResult) => {
        // Preencher o campo de código com o QRCode decodificado
        document.getElementById('codigo').value = decodedText;
        
        window.location.href = "../validarQR/" + encodeURIComponent(decodedText) + "/";
        html5QrCode.stop(); // Para a câmera após leitura
    };

    const config = { fps: 10, qrbox: 250 }; // Configurações da câmera
    html5QrCode.start({ facingMode: "environment" }, config, qrCodeSuccessCallback)
        .catch(err => {
            console.error("Erro ao iniciar o leitor de QR Code:", err);
        });
});

