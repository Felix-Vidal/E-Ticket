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

// Enviar para a view do Django ao clicar no botão "Avançar"
document.getElementById('btn-avancar').addEventListener('click', function () {
    const codigo = document.getElementById('codigo').value;

    fetch("{% url 'validarQR' %}", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // Importante para segurança no Django
        },
        body: JSON.stringify({ codigo: codigo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("QR Code validado e créditos deduzidos!");
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Erro:', error));
});