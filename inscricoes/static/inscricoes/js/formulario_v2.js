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

    // Função para formatar data no padrão dd/mm/yyyy
    function formatarDataNascimento(campo) {
        let valor = campo.value.replace(/\D/g, '');

        if (valor.length > 8) {
            valor = valor.substring(0, 8);
        }

        if (valor.length >= 5) {
            campo.value = `${valor.substring(0, 2)}/${valor.substring(2, 4)}/${valor.substring(4)}`;
        } else if (valor.length === 4) {
            campo.value = `${valor.substring(0, 2)}/${valor.substring(2, 4)}/`;
        } else if (valor.length >= 3) {
            campo.value = `${valor.substring(0, 2)}/${valor.substring(2)}`;
        } else if (valor.length === 2) {
            campo.value = `${valor}/`;
        } else {
            campo.value = valor;
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

    // Aplica formatação à data de nascimento
    const campoDataNascimento = document.getElementById('id_data_nascimento');
    if (campoDataNascimento) {
        ['input', 'keyup', 'blur', 'paste'].forEach(function(eventName) {
            campoDataNascimento.addEventListener(eventName, function() {
                formatarDataNascimento(this);
            });
        });
    }

    const cacheTurmasPorCurso = new Map();
    let requisicaoTurmasController = null;
    let preCargaTurmasIniciada = false;

    function normalizarTexto(valor) {
        return (valor || '')
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');
    }

    function obterRotuloTurma(cursoNome, turmaNome, totalTurmas, indiceTurma) {
        const cursoNormalizado = normalizarTexto(cursoNome);
        const turmaNormalizada = normalizarTexto(turmaNome);
        const isViolao = cursoNormalizado.includes('violao');
        const usaPadraoInicianteAvancado = ['teatro', 'teclado']
            .some(nomeCurso => cursoNormalizado.includes(nomeCurso));

        if (isViolao) {
            if (turmaNormalizada.includes('infantil') || turmaNormalizada.includes('iniciante')) {
                return 'Turma 1 Infantil';
            }
            if (turmaNormalizada.includes('adult') || turmaNormalizada.includes('avancad')) {
                return 'Turma 2 Aduldo';
            }
            if (cursoNormalizado.includes('infantil') || cursoNormalizado.includes('iniciante')) {
                return 'Turma 1 Infantil';
            }
            if (cursoNormalizado.includes('adult') || cursoNormalizado.includes('avancad')) {
                return 'Turma 2 Aduldo';
            }
            if (totalTurmas > 1) {
                if (indiceTurma === 0) {
                    return 'Turma 1 Infantil';
                }
                if (indiceTurma === 1) {
                    return 'Turma 2 Aduldo';
                }
                return `Turma ${indiceTurma + 1}`;
            }
        }

        if (turmaNormalizada.includes('iniciante')) {
            return 'Turma 1 Iniciante';
        }
        if (turmaNormalizada.includes('avancad')) {
            return 'Turma 2 Avançado';
        }
        if (cursoNormalizado.includes('iniciante')) {
            return 'Turma 1 Iniciante';
        }
        if (cursoNormalizado.includes('avancad')) {
            return 'Turma 2 Avançado';
        }

        if (usaPadraoInicianteAvancado && totalTurmas > 1) {
            if (indiceTurma === 0) {
                return 'Turma 1 Iniciante';
            }
            if (indiceTurma === 1) {
                return 'Turma 2 Avançado';
            }
            return `Turma ${indiceTurma + 1}`;
        }

        if (totalTurmas <= 1) {
            return 'Turma Única';
        }

        return `Turma ${indiceTurma + 1}`;
    }

    function formatarRotuloCurso(rotuloOriginal) {
        const cursoNormalizado = normalizarTexto(rotuloOriginal);

        if (cursoNormalizado.includes('teatro') && cursoNormalizado.includes('iniciante')) {
            return 'TEATRO (TURMA 1 INICIANTE)';
        }
        if (cursoNormalizado.includes('teatro') && cursoNormalizado.includes('avancad')) {
            return 'TEATRO (TURMA 2 AVANÇADO)';
        }
        if (cursoNormalizado.includes('teclado') && cursoNormalizado.includes('iniciante')) {
            return 'TECLADO (TURMA 1 INICIANTE)';
        }
        if (cursoNormalizado.includes('teclado') && cursoNormalizado.includes('avancad')) {
            return 'TECLADO (TURMA 2 AVANÇADO)';
        }
        if (cursoNormalizado.includes('violao') && (cursoNormalizado.includes('infantil') || cursoNormalizado.includes('iniciante'))) {
            return 'VIOLÃO (TURMA 1 INFANTIL)';
        }
        if (cursoNormalizado.includes('violao') && (cursoNormalizado.includes('adult') || cursoNormalizado.includes('avancad'))) {
            return 'VIOLÃO (TURMA 2 ADULDO)';
        }

        return rotuloOriginal;
    }

    function obterClasseTemaCurso(rotuloOriginal) {
        const cursoNormalizado = normalizarTexto(rotuloOriginal);

        if (cursoNormalizado.includes('capoeira')) {
            return 'theme-capoeira';
        }
        if (cursoNormalizado.includes('teatro')) {
            return 'theme-teatro';
        }
        if (cursoNormalizado.includes('danca do ventre') || cursoNormalizado.includes('ventre') || cursoNormalizado.includes('danca popular')) {
            return 'theme-danca-ventre';
        }
        if (cursoNormalizado.includes('danca moderna')) {
            return 'theme-danca-moderna';
        }
        if (cursoNormalizado.includes('bale') || cursoNormalizado.includes('ballet')) {
            return 'theme-ballet';
        }
        if (cursoNormalizado.includes('violao')) {
            return 'theme-violao';
        }
        if (cursoNormalizado.includes('teclado')) {
            return 'theme-teclado';
        }
        if (cursoNormalizado.includes('bateria')) {
            return 'theme-bateria';
        }
        if (cursoNormalizado.includes('percussao')) {
            return 'theme-percussao';
        }

        return '';
    }

    function obterPrioridadeTurma(cursoNome, turmaNome) {
        const cursoNormalizado = normalizarTexto(cursoNome);
        const turmaNormalizada = normalizarTexto(turmaNome);

        if (cursoNormalizado.includes('violao')) {
            if (turmaNormalizada.includes('infantil') || turmaNormalizada.includes('iniciante')) {
                return 1;
            }
            if (turmaNormalizada.includes('adult') || turmaNormalizada.includes('avancad')) {
                return 2;
            }
        }

        if (cursoNormalizado.includes('teatro') || cursoNormalizado.includes('teclado')) {
            if (turmaNormalizada.includes('iniciante')) {
                return 1;
            }
            if (turmaNormalizada.includes('avancad')) {
                return 2;
            }
        }

        return 99;
    }

    function aplicarRotulosNosCursos() {
        const cursosContainer = document.getElementById('cursos-container');
        if (!cursosContainer) {
            return;
        }

        const themeClasses = [
            'theme-capoeira',
            'theme-teatro',
            'theme-danca-ventre',
            'theme-danca-moderna',
            'theme-ballet',
            'theme-violao',
            'theme-teclado',
            'theme-bateria',
            'theme-percussao'
        ];

        const items = cursosContainer.querySelectorAll('.curso-item');
        items.forEach(item => {
            const label = item.querySelector('.form-check-label');
            if (!label) {
                return;
            }

            if (!label.dataset.originalLabel) {
                label.dataset.originalLabel = label.textContent.trim();
            }

            label.textContent = formatarRotuloCurso(label.dataset.originalLabel);

            item.classList.remove(...themeClasses);
            const classeTema = obterClasseTemaCurso(label.dataset.originalLabel);
            if (classeTema) {
                item.classList.add(classeTema);
            }
        });
    }

    // Função para renderizar as turmas dentro do bloco de cada curso.
    function renderizarTurmasInline(turmas, selecionadasAntes) {
        const cursosContainer = document.getElementById('cursos-container');
        if (!cursosContainer) {
            return;
        }
        const cursoItems = cursosContainer.querySelectorAll('.curso-item');
        const turmasPorCurso = {};

        turmas.forEach(turma => {
            if (!turmasPorCurso[turma.curso_id]) {
                turmasPorCurso[turma.curso_id] = [];
            }
            turmasPorCurso[turma.curso_id].push(turma);
        });

        cursoItems.forEach(item => {
            const checkboxCurso = item.querySelector('input[type="checkbox"][name="cursos"]');
            const turmasCursoContainer = item.querySelector('.turmas-curso');

            if (!checkboxCurso || !turmasCursoContainer) {
                return;
            }

            turmasCursoContainer.innerHTML = '';

            if (!checkboxCurso.checked) {
                turmasCursoContainer.classList.add('d-none');
                return;
            }

            turmasCursoContainer.classList.remove('d-none');

            const cursoId = Number(checkboxCurso.value);
            const turmasDoCurso = turmasPorCurso[cursoId] || [];
            const turmasOrdenadas = [...turmasDoCurso].sort((a, b) => {
                const prioridadeA = obterPrioridadeTurma(a.curso_nome, a.nome);
                const prioridadeB = obterPrioridadeTurma(b.curso_nome, b.nome);

                if (prioridadeA !== prioridadeB) {
                    return prioridadeA - prioridadeB;
                }

                const horarioA = String(a.horario_inicio || '');
                const horarioB = String(b.horario_inicio || '');
                if (horarioA !== horarioB) {
                    return horarioA.localeCompare(horarioB);
                }

                return String(a.nome || '').localeCompare(String(b.nome || ''));
            });

            if (turmasOrdenadas.length === 0) {
                turmasCursoContainer.innerHTML = '<p class="text-muted mb-0 small">Nenhuma turma disponivel para este curso.</p>';
                return;
            }

            turmasOrdenadas.forEach((turma, indiceTurma) => {
                const checked = selecionadasAntes.has(String(turma.id)) ? 'checked' : '';
                const turmaIds = Array.isArray(turma.ids) && turma.ids.length > 0
                    ? turma.ids.join(',')
                    : String(turma.id);
                const rotuloTurma = obterRotuloTurma(turma.curso_nome, turma.nome, turmasOrdenadas.length, indiceTurma);
                const nomeTurmaNormalizado = normalizarTexto(turma.nome);
                const complementoNomeTurma = nomeTurmaNormalizado === 'turma unica' ? '' : `: ${turma.nome}`;
                const bloco = document.createElement('div');
                bloco.className = 'form-check mb-2';
                bloco.innerHTML = `
                    <input class="form-check-input turma-checkbox" type="checkbox" name="turmas" value="${turma.id}" id="turma${turma.id}" data-curso-id="${turma.curso_id}" data-turma-ids="${turmaIds}" ${checked}>
                    <label class="form-check-label" for="turma${turma.id}">
                        ${rotuloTurma}${complementoNomeTurma} (${turma.dia_semana} ${turma.horario_inicio}-${turma.horario_fim}) (${turma.vagas_disponiveis} vagas)
                    </label>
                `;
                turmasCursoContainer.appendChild(bloco);
            });

            const marcadasNoCurso = turmasCursoContainer.querySelectorAll('.turma-checkbox:checked');
            if (marcadasNoCurso.length > 0) {
                const escolhida = marcadasNoCurso[0];
                turmasCursoContainer.querySelectorAll('.turma-checkbox').forEach(checkbox => {
                    if (checkbox !== escolhida) {
                        checkbox.disabled = true;
                    }
                });
            }
        });

        atualizarTurmasSelecionadas();
    }

    function obterTurmasDoCache(cursosSelecionados) {
        const turmas = [];
        cursosSelecionados.forEach(cursoId => {
            const turmasCurso = cacheTurmasPorCurso.get(Number(cursoId)) || [];
            turmas.push(...turmasCurso);
        });
        return turmas;
    }

    function preencherCacheTurmas(cursoIds, turmas) {
        const turmasPorCurso = {};
        cursoIds.forEach(cursoId => {
            turmasPorCurso[cursoId] = [];
        });

        turmas.forEach(turma => {
            if (!turmasPorCurso[turma.curso_id]) {
                turmasPorCurso[turma.curso_id] = [];
            }
            turmasPorCurso[turma.curso_id].push(turma);
        });

        cursoIds.forEach(cursoId => {
            cacheTurmasPorCurso.set(Number(cursoId), turmasPorCurso[cursoId] || []);
        });
    }

    function preCarregarTurmasEmBackground(cursosCheckboxes) {
        if (preCargaTurmasIniciada) {
            return;
        }

        const todosCursosIds = Array.from(cursosCheckboxes).map(checkbox => checkbox.value);
        const cursosSemCache = todosCursosIds.filter(cursoId => !cacheTurmasPorCurso.has(Number(cursoId)));
        if (cursosSemCache.length === 0) {
            return;
        }

        preCargaTurmasIniciada = true;
        const agendar = window.requestIdleCallback || function(callback) {
            return setTimeout(callback, 220);
        };

        agendar(function() {
            const url = `/inscricoes/get_turmas/?curso_id=${cursosSemCache.join(',')}`;
            fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erro do servidor: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    preencherCacheTurmas(cursosSemCache, data.turmas || []);
                })
                .catch(error => {
                    console.warn('Pré-carga de turmas não concluída:', error.message);
                    preCargaTurmasIniciada = false;
                });
        });
    }

    function exibirCarregandoNosCursos(cursosIds) {
        const cursosContainer = document.getElementById('cursos-container');
        if (!cursosContainer || cursosIds.length === 0) {
            return;
        }

        const idsSet = new Set(cursosIds.map(id => String(id)));
        cursosContainer.querySelectorAll('.curso-item').forEach(item => {
            const checkboxCurso = item.querySelector('input[type="checkbox"][name="cursos"]');
            const turmasCursoContainer = item.querySelector('.turmas-curso');
            if (!checkboxCurso || !checkboxCurso.checked || !turmasCursoContainer) {
                return;
            }

            if (!idsSet.has(String(checkboxCurso.value))) {
                return;
            }

            turmasCursoContainer.classList.remove('d-none');
            turmasCursoContainer.innerHTML = '<p class="text-muted mb-0 small">Carregando turmas...</p>';
        });
    }

    // Função para carregar turmas dos cursos marcados e exibir inline.
    function carregarTurmasInline() {
        const cursosContainer = document.getElementById('cursos-container');
        if (!cursosContainer) {
            return;
        }

        const cursosCheckboxes = cursosContainer.querySelectorAll('input[type="checkbox"][name="cursos"]');
        const cursosSelecionados = Array.from(cursosCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        const selecionadasAntes = new Set(
            Array.from(document.querySelectorAll('.turma-checkbox:checked')).map(checkbox => checkbox.value)
        );

        if (cursosSelecionados.length === 0) {
            cursosContainer.querySelectorAll('.turmas-curso').forEach(turmaContainer => {
                turmaContainer.classList.add('d-none');
                turmaContainer.innerHTML = '';
            });
            atualizarTurmasSelecionadas();
            return;
        }

        const cursosSemCache = cursosSelecionados.filter(cursoId => !cacheTurmasPorCurso.has(Number(cursoId)));
        const turmasCache = obterTurmasDoCache(cursosSelecionados);
        renderizarTurmasInline(turmasCache, selecionadasAntes);

        if (cursosSemCache.length === 0) {
            return;
        }

        exibirCarregandoNosCursos(cursosSemCache);

        if (requisicaoTurmasController) {
            requisicaoTurmasController.abort();
        }

        requisicaoTurmasController = new AbortController();
        const controllerAtual = requisicaoTurmasController;

        const url = `/inscricoes/get_turmas/?curso_id=${cursosSemCache.join(',')}`;
        fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin',
            signal: controllerAtual.signal
        })
            .then(response => {
                if (response.status === 403) {
                    throw new Error('Você precisa estar logado para ver as turmas.');
                }
                if (response.status === 404) {
                    throw new Error('Página não encontrada.');
                }
                if (!response.ok) {
                    throw new Error(`Erro do servidor: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const turmas = data.turmas || [];
                preencherCacheTurmas(cursosSemCache, turmas);

                const cursosAindaSelecionados = Array.from(cursosContainer.querySelectorAll('input[type="checkbox"][name="cursos"]'))
                    .filter(checkbox => checkbox.checked)
                    .map(checkbox => checkbox.value);

                renderizarTurmasInline(obterTurmasDoCache(cursosAindaSelecionados), selecionadasAntes);
            })
            .catch(error => {
                if (error.name === 'AbortError') {
                    return;
                }

                console.error('Erro ao carregar turmas:', error);
                cursosContainer.querySelectorAll('.curso-item').forEach(item => {
                    const checkboxCurso = item.querySelector('input[type="checkbox"][name="cursos"]');
                    const turmasCursoContainer = item.querySelector('.turmas-curso');
                    if (
                        checkboxCurso &&
                        checkboxCurso.checked &&
                        turmasCursoContainer &&
                        cursosSemCache.includes(checkboxCurso.value)
                    ) {
                        turmasCursoContainer.classList.remove('d-none');
                        turmasCursoContainer.innerHTML = `<p class="text-danger mb-0 small">Erro ao carregar turmas: ${error.message}</p>`;
                    }
                });
                atualizarTurmasSelecionadas();
            })
            .finally(() => {
                if (requisicaoTurmasController === controllerAtual) {
                    requisicaoTurmasController = null;
                }
            });
    }

    // Adiciona evento aos checkboxes de cursos
    const cursosContainer = document.getElementById('cursos-container');
    if (cursosContainer) {
        aplicarRotulosNosCursos();
        const cursosCheckboxes = cursosContainer.querySelectorAll('input[type="checkbox"][name="cursos"]');
        cursosCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', carregarTurmasInline);
        });

        preCarregarTurmasEmBackground(cursosCheckboxes);

        if (Array.from(cursosCheckboxes).some(checkbox => checkbox.checked)) {
            carregarTurmasInline();
        }
    }

    // Função para atualizar o campo oculto com as turmas selecionadas
    function atualizarTurmasSelecionadas() {
        const turmasCheckboxes = document.querySelectorAll('.turma-checkbox:checked');
        const turmasSelecionadas = new Set();

        Array.from(turmasCheckboxes).forEach(checkbox => {
            const idsAgrupados = checkbox.getAttribute('data-turma-ids');
            if (!idsAgrupados) {
                turmasSelecionadas.add(checkbox.value);
                return;
            }

            idsAgrupados
                .split(',')
                .map(id => id.trim())
                .filter(id => id.length > 0)
                .forEach(id => turmasSelecionadas.add(id));
        });

        document.getElementById('turmas_selecionadas').value = Array.from(turmasSelecionadas).join(',');
        console.log('Turmas selecionadas:', turmasSelecionadas);
    }

    // Mantem compatibilidade com chamadas inline do template.
    window.atualizarTurmasSelecionadas = atualizarTurmasSelecionadas;

    // Adiciona evento para atualizar as turmas selecionadas quando um checkbox é marcado/desmarcado
    document.addEventListener('change', function(event) {
        if (!event.target.classList.contains('turma-checkbox')) {
            return;
        }

        const checkboxAtual = event.target;
        const cursoId = checkboxAtual.getAttribute('data-curso-id');
        const containerCurso = checkboxAtual.closest('.turmas-curso');
        if (!containerCurso) {
            atualizarTurmasSelecionadas();
            return;
        }

        const checkboxesCurso = containerCurso.querySelectorAll(`.turma-checkbox[data-curso-id="${cursoId}"]`);
        if (checkboxAtual.checked) {
            checkboxesCurso.forEach(checkbox => {
                if (checkbox !== checkboxAtual) {
                    checkbox.checked = false;
                    checkbox.disabled = true;
                }
            });
        } else {
            checkboxesCurso.forEach(checkbox => {
                checkbox.disabled = false;
            });
        }

        atualizarTurmasSelecionadas();
    });
    
    // Adiciona validação ao formulário antes do envio
    const formulario = document.querySelector('form');
    if (formulario) {
        formulario.addEventListener('submit', function(event) {
            // Recalcula no submit para não depender da ordem dos listeners.
            atualizarTurmasSelecionadas();

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