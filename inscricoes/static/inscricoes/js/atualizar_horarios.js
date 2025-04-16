document.addEventListener('DOMContentLoaded', function() {
    const cursosCheckboxes = document.querySelectorAll('input[name="cursos"]');
    const horariosContainer = document.querySelector('.col-md-12:last-child .border.rounded.p-3');
    
    // Desabilita os checkboxes de horários inicialmente
    if (horariosContainer) {
        horariosContainer.style.opacity = '0.5';
        horariosContainer.style.pointerEvents = 'none';
    }
    
    function atualizarHorarios() {
        const cursosSelecionados = Array.from(cursosCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        
        if (cursosSelecionados.length === 0) {
            if (horariosContainer) {
                horariosContainer.style.opacity = '0.5';
                horariosContainer.style.pointerEvents = 'none';
            }
            return;
        }

        // Faz uma requisição AJAX para obter os horários disponíveis
        fetch(`/inscricoes/get_turmas/?curso_id=${cursosSelecionados.join(',')}`)
            .then(response => response.json())
            .then(data => {
                if (horariosContainer) {
                    horariosContainer.innerHTML = '';
                    
                    if (data.turmas && data.turmas.length > 0) {
                        // Agrupa turmas por curso
                        const turmasPorCurso = {};
                        data.turmas.forEach(turma => {
                            if (!turmasPorCurso[turma.curso_id]) {
                                turmasPorCurso[turma.curso_id] = [];
                            }
                            turmasPorCurso[turma.curso_id].push(turma);
                        });

                        // Cria os checkboxes para cada turma
                        Object.entries(turmasPorCurso).forEach(([cursoId, turmas]) => {
                            const cursoDiv = document.createElement('div');
                            cursoDiv.className = 'mb-3';
                            
                            const cursoLabel = document.createElement('div');
                            cursoLabel.className = 'fw-bold text-primary mb-2';
                            cursoLabel.textContent = turmas[0].curso_nome;
                            cursoDiv.appendChild(cursoLabel);

                            turmas.forEach(turma => {
                                const div = document.createElement('div');
                                div.className = 'form-check';
                                
                                const input = document.createElement('input');
                                input.type = 'checkbox';
                                input.name = 'horarios_selecionados';
                                input.value = turma.id;
                                input.className = 'form-check-input turma-checkbox';
                                input.id = `horario_${turma.id}`;
                                input.dataset.cursoId = turma.curso_id;

                                // Desabilita o checkbox se as vagas acabaram
                                if (turma.vagas_disponiveis === 0){
                                    input.disabled = true;
                                    div.style.opacity = '0.5'; // Para dar a sensação de que está desabilitado
                                }
                                
                                const label = document.createElement('label');
                                label.className = 'form-check-label';
                                label.htmlFor = `horario_${turma.id}`;
                                
                                let labelText = `${turma.nome} - ${turma.dia_semana} (${turma.horario_inicio} - ${turma.horario_fim}) - Vagas: ${turma.vagas_disponiveis}`;
                                if(turma.vagas_disponiveis === 0){
                                    labelText += ' (Esgotado)';
                                }
                                label.textContent = labelText;
                                
                                div.appendChild(input);
                                div.appendChild(label);
                                cursoDiv.appendChild(div);
                            });

                            horariosContainer.appendChild(cursoDiv);
                        });
                        
                        // Adiciona evento para desabilitar outras turmas do mesmo curso
                        const turmaCheckboxes = horariosContainer.querySelectorAll('.turma-checkbox');
                        turmaCheckboxes.forEach(checkbox => {
                            checkbox.addEventListener('change', function() {
                                const cursoId = this.dataset.cursoId;
                                turmaCheckboxes.forEach(otherCheckbox => {
                                    if (otherCheckbox !== this && otherCheckbox.dataset.cursoId === cursoId) {
                                        otherCheckbox.disabled = this.checked;
                                        otherCheckbox.parentElement.style.opacity = this.checked ? '0.5' : '1';
                                    }
                                });
                            });
                        });
                        
                        horariosContainer.style.opacity = '1';
                        horariosContainer.style.pointerEvents = 'auto';
                    } else {
                        horariosContainer.innerHTML = '<p class="text-danger">Não há vagas disponíveis para os cursos selecionados.</p>';
                        horariosContainer.style.opacity = '0.5';
                        horariosContainer.style.pointerEvents = 'none';
                    }
                }
            })
            .catch(error => {
                console.error('Erro ao buscar horários:', error);
                if (horariosContainer) {
                    horariosContainer.innerHTML = '<p class="text-danger">Erro ao carregar horários. Por favor, tente novamente.</p>';
                }
            });
    }
    
    // Adiciona o evento de change para cada checkbox de curso
    cursosCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', atualizarHorarios);
    });
}); 