document.addEventListener("DOMContentLoaded", function () {
    const btnAvancar = document.getElementById('btn-avancar');

    btnAvancar.addEventListener('click', function () {
        // Captura o valor do campo de entrada
        const codigo = document.getElementById('codigo').value;

        // Verifica se o campo não está vazio
        if (codigo) {
            // Constrói a URL com o código do input
            const url = `../validarQR/${encodeURIComponent(codigo)}/`;

            // Redireciona para a URL
            window.location.href = url;
        } else {
            alert("Por favor, digite um código válido."); // Mensagem de alerta se o campo estiver vazio
        }
    });
});