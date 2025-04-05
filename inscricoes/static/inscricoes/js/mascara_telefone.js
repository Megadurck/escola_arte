document.addEventListener('DOMContentLoaded', function() {
    // Função para aplicar máscara de CPF
    function mascaraCPF(cpf) {
        cpf = cpf.replace(/\D/g, '');
        cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
        cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
        cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        return cpf;
    }

    // Função para aplicar máscara de telefone
    function mascaraTelefone(telefone) {
        telefone = telefone.replace(/\D/g, '');
        telefone = telefone.replace(/^(\d{2})(\d)/g, '($1) $2');
        telefone = telefone.replace(/(\d)(\d{4})$/, '$1-$2');
        return telefone;
    }

    // Aplica máscara ao campo de CPF
    const campoCPF = document.querySelector('input[name="cpf"]');
    if (campoCPF) {
        campoCPF.addEventListener('input', function(e) {
            let valor = e.target.value;
            valor = mascaraCPF(valor);
            e.target.value = valor;
        });
    }

    // Aplica máscara ao campo de telefone
    const campoTelefone = document.querySelector('input[name="telefone_whatsapp"]');
    if (campoTelefone) {
        campoTelefone.addEventListener('input', function(e) {
            let valor = e.target.value;
            valor = mascaraTelefone(valor);
            e.target.value = valor;
        });
    }

    // Validação do formulário antes do envio
    const form = document.getElementById('inscricaoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            let valid = true;
            const mensagensErro = [];

            // Validação do CPF
            const cpf = campoCPF.value.replace(/\D/g, '');
            if (cpf.length !== 11) {
                mensagensErro.push('CPF deve conter 11 dígitos');
                valid = false;
            }

            // Validação do telefone
            const telefone = campoTelefone.value.replace(/\D/g, '');
            if (telefone.length !== 11) {
                mensagensErro.push('Telefone deve conter 11 dígitos (DDD + número)');
                valid = false;
            }

            // Validação dos cursos selecionados
            const cursosCheckboxes = document.querySelectorAll('input[name="cursos"]:checked');
            if (cursosCheckboxes.length === 0) {
                mensagensErro.push('Selecione pelo menos um curso');
                valid = false;
            }

            // Validação dos horários selecionados
            const horariosCheckboxes = document.querySelectorAll('input[name="horarios_selecionados"]:checked');
            if (horariosCheckboxes.length === 0) {
                mensagensErro.push('Selecione pelo menos um horário');
                valid = false;
            }

            if (!valid) {
                e.preventDefault();
                alert('Por favor, corrija os seguintes erros:\n' + mensagensErro.join('\n'));
            }
        });
    }
}); 