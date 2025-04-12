document.addEventListener('DOMContentLoaded', function() {
    console.log('Formulário carregado - TESTE DE LOG');
    
    // Função para formatar CPF
    function formatarCPF(campo) {
        // Remove todos os caracteres não numéricos
        let valor = campo.value.replace(/\D/g, '');
        
        // Limita a 11 dígitos (apenas números)
        if (valor.length > 11) {
            valor = valor.substring(0, 11);
        }
        
        // Formata o número para exibição
        if (valor.length > 0) {
            let cpfFormatado = '';
            
            // Adiciona os pontos e hífen
            if (valor.length > 3) {
                cpfFormatado = valor.substring(0, 3) + '.';
                
                if (valor.length > 6) {
                    cpfFormatado += valor.substring(3, 6) + '.';
                    
                    if (valor.length > 9) {
                        cpfFormatado += valor.substring(6, 9) + '-';
                        cpfFormatado += valor.substring(9);
                    } else {
                        cpfFormatado += valor.substring(6);
                    }
                } else {
                    cpfFormatado += valor.substring(3);
                }
            } else {
                cpfFormatado = valor;
            }
            
            // Atualiza o valor do campo com a formatação
            campo.value = cpfFormatado;
        }
    }

    // Função para formatar telefone
    function formatarTelefone(campo) {
        // Remove todos os caracteres não numéricos
        let valor = campo.value.replace(/\D/g, '');
        
        // Limita a 11 dígitos (apenas números)
        if (valor.length > 11) {
            valor = valor.substring(0, 11);
        }
        
        // Formata o número para exibição
        if (valor.length > 0) {
            let numeroFormatado = '';
            
            // Adiciona o DDD entre parênteses
            numeroFormatado = '(' + valor.substring(0, 2);
            
            if (valor.length > 2) {
                numeroFormatado += ') ';
                
                // Se tiver 11 dígitos (com 9), formata de uma maneira
                if (valor.length === 11) {
                    numeroFormatado += valor.substring(2, 3) + ' ' + // 9
                                    valor.substring(3, 7) + '-' +    // xxxx
                                    valor.substring(7);               // xxxx
                } else {
                    // Se tiver 10 dígitos (sem 9), formata de outra maneira
                    numeroFormatado += valor.substring(2, 6) + '-' + // xxxx
                                    valor.substring(6);               // xxxx
                }
            }
            
            // Atualiza o valor do campo com a formatação
            campo.value = numeroFormatado;
        }
    }

    // Aplica formatação ao CPF
    const campoCPF = document.getElementById('id_cpf');
    if (campoCPF) {
        console.log('Campo CPF encontrado');
        campoCPF.addEventListener('input', function() {
            formatarCPF(this);
        });
    } else {
        console.log('Campo CPF NÃO encontrado');
    }

    // Aplica formatação ao telefone
    const campoTelefone = document.getElementById('id_telefone_whatsapp');
    if (campoTelefone) {
        console.log('Campo telefone encontrado');
        campoTelefone.addEventListener('input', function() {
            formatarTelefone(this);
        });
    } else {
        console.log('Campo telefone NÃO encontrado');
    }

    // Função para carregar horários
    function carregarHorarios() {
        console.log('Carregando horários - TESTE DE LOG');
        
        // Verifica se o container de cursos existe
        const cursosContainer = document.getElementById('cursos-container');
        if (!cursosContainer) {
            console.error('Container de cursos não encontrado!');
            return;
        }
        
        // Busca todos os checkboxes de cursos dentro do container
        const cursosCheckboxes = cursosContainer.querySelectorAll('input[type="checkbox"]');
        console.log('Checkboxes de cursos encontrados:', cursosCheckboxes.length);
        
        const cursosSelecionados = Array.from(cursosCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        
        console.log('Cursos selecionados:', cursosSelecionados);
        
        if (cursosSelecionados.length === 0) {
            document.getElementById('horarios-container').innerHTML = '<p class="text-muted">Selecione pelo menos um curso para ver os horários disponíveis.</p>';
            return;
        }

        const url = `/inscricoes/get_turmas/?curso_id=${cursosSelecionados.join(',')}`;
        console.log('URL:', url);
        
        fetch(url)
            .then(response => {
                console.log('Resposta:', response);
                return response.json();
            })
            .then(data => {
                console.log('Dados:', data);
                const container = document.getElementById('horarios-container');
                container.innerHTML = '';
                
                if (data.turmas && data.turmas.length > 0) {
                    // Agrupa turmas por curso
                    const turmasPorCurso = {};
                    data.turmas.forEach(turma => {
                        if (!turmasPorCurso[turma.curso_id]) {
                            turmasPorCurso[turma.curso_id] = {
                                nome: turma.curso_nome,
                                turmas: []
                            };
                        }
                        turmasPorCurso[turma.curso_id].turmas.push(turma);
                    });
                    
                    // Cria elementos para cada curso
                    Object.keys(turmasPorCurso).forEach(cursoId => {
                        const curso = turmasPorCurso[cursoId];
                        
                        // Adiciona o título do curso
                        const cursoTitle = document.createElement('h5');
                        cursoTitle.className = 'mt-3 mb-2 text-primary';
                        cursoTitle.textContent = curso.nome;
                        container.appendChild(cursoTitle);
                        
                        // Adiciona as turmas do curso
                        curso.turmas.forEach(turma => {
                            const div = document.createElement('div');
                            div.className = 'form-check mb-2';
                            div.innerHTML = `
                                <input class="form-check-input turma-checkbox" type="checkbox" name="turmas" 
                                       value="${turma.id}" id="turma${turma.id}" data-curso-id="${turma.curso_id}">
                                <label class="form-check-label" for="turma${turma.id}">
                                    ${turma.nome} (${turma.dia_semana} ${turma.horario_inicio}-${turma.horario_fim}) 
                                    (${turma.vagas_disponiveis} vagas)
                                </label>
                            `;
                            container.appendChild(div);
                        });
                    });
                    
                    // Adiciona evento para desabilitar turmas do mesmo curso
                    const turmasCheckboxes = container.querySelectorAll('.turma-checkbox');
                    turmasCheckboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', function() {
                            const cursoId = this.getAttribute('data-curso-id');
                            
                            // Se este checkbox foi marcado, desabilita os outros do mesmo curso
                            if (this.checked) {
                                turmasCheckboxes.forEach(otherCheckbox => {
                                    if (otherCheckbox !== this && otherCheckbox.getAttribute('data-curso-id') === cursoId) {
                                        otherCheckbox.disabled = true;
                                        otherCheckbox.checked = false;
                                    }
                                });
                            } else {
                                // Se este checkbox foi desmarcado, habilita os outros do mesmo curso
                                turmasCheckboxes.forEach(otherCheckbox => {
                                    if (otherCheckbox.getAttribute('data-curso-id') === cursoId) {
                                        otherCheckbox.disabled = false;
                                    }
                                });
                            }
                            
                            // Atualiza o campo oculto com os IDs das turmas selecionadas
                            atualizarTurmasSelecionadas();
                        });
                    });
                } else {
                    container.innerHTML = '<p class="text-muted">Nenhum horário disponível para os cursos selecionados.</p>';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar horários:', error);
                document.getElementById('horarios-container').innerHTML = '<p class="text-danger">Erro ao carregar horários. Por favor, tente novamente.</p>';
            });
    }

    // Adiciona evento aos checkboxes de cursos
    const cursosContainer = document.getElementById('cursos-container');
    if (cursosContainer) {
        console.log('Container de cursos encontrado');
        const cursosCheckboxes = cursosContainer.querySelectorAll('input[type="checkbox"]');
        console.log('Checkboxes de cursos encontrados:', cursosCheckboxes.length);
        
        if (cursosCheckboxes.length === 0) {
            console.log('Nenhum checkbox de curso encontrado!');
        } else {
            cursosCheckboxes.forEach(checkbox => {
                console.log('Adicionando evento ao checkbox:', checkbox.id);
                checkbox.addEventListener('change', carregarHorarios);
            });
        }
    } else {
        console.error('Container de cursos não encontrado!');
    }

    // Função para atualizar o campo oculto com as turmas selecionadas
    function atualizarTurmasSelecionadas() {
        const turmasCheckboxes = document.querySelectorAll('.turma-checkbox:checked');
        const turmasSelecionadas = Array.from(turmasCheckboxes).map(checkbox => checkbox.value);
        document.getElementById('turmas_selecionadas').value = turmasSelecionadas.join(',');
        console.log('Turmas selecionadas:', turmasSelecionadas);
    }

    // Adiciona evento para atualizar as turmas selecionadas quando um checkbox é marcado/desmarcado
    document.addEventListener('change', function(event) {
        if (event.target.classList.contains('turma-checkbox')) {
            atualizarTurmasSelecionadas();
        }
    });
    
    // Adiciona validação ao formulário antes do envio
    const formulario = document.querySelector('form');
    if (formulario) {
        formulario.addEventListener('submit', function(event) {
            const turmasSelecionadas = document.getElementById('turmas_selecionadas').value;
            
            if (!turmasSelecionadas) {
                event.preventDefault();
                alert('Você deve selecionar pelo menos uma turma para se inscrever.');
                return false;
            }
            
            return true;
        });
    }
}); 