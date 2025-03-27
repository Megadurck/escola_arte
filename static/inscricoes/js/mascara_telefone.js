document.addEventListener("DOMContentLoaded", function() {
    const telefoneInput = document.getElementById('id_telefone_whatsapp');

    telefoneInput.addEventListener('input', function(e) {
        let telefone = e.target.value.replace(/\D/g, ''); // Remove tudo que não for número

        if (telefone.length <= 10) {
            telefone = telefone.replace(/^(\d{2})(\d{0,5})(\d{0,4})$/, '($1) $2-$3');
        } else {
            telefone = telefone.replace(/^(\d{2})(\d{0,5})(\d{0,4})$/, '($1) $2-$3');
        }

        e.target.value = telefone; // Aplica a máscara
    });
});


