// Funções para a galeria de imagens
function openGallery(courseId) {
    // Esconde todas as galerias
    document.querySelectorAll('.gallery-container').forEach(gallery => {
        gallery.style.display = 'none';
    });
    
    // Mostra a galeria selecionada
    const selectedGallery = document.getElementById(`gallery-${courseId}`);
    if (selectedGallery) {
        selectedGallery.style.display = 'block';
    }
}

function closeGallery(courseId) {
    const gallery = document.getElementById(`gallery-${courseId}`);
    if (gallery) {
        gallery.style.display = 'none';
    }
}

function changeImage(index, courseId) {
    const gallery = document.getElementById(`gallery-${courseId}`);
    if (gallery) {
        const mainImage = gallery.querySelector('.main-image');
        const images = gallery.querySelectorAll('.gallery-item img');
        if (mainImage && images[index]) {
            mainImage.src = images[index].src;
        }
    }
}

// Funções para carregar turmas
function loadTurmas(cursoId) {
    const turmasContainer = document.getElementById('turmas-container');
    const turmasField = document.getElementById('id_turmas');
    
    // Limpa as turmas anteriores
    turmasContainer.innerHTML = '';
    turmasField.innerHTML = '';
    
    // Faz a requisição para obter as turmas do curso
    fetch(`/inscricoes/get_turmas/${cursoId}/`)
        .then(response => response.json())
        .then(data => {
            data.turmas.forEach(turma => {
                // Adiciona a opção ao select de turmas
                const option = document.createElement('option');
                option.value = turma.id;
                option.textContent = `${turma.nome} - ${turma.dia_semana} (${turma.horario_inicio} - ${turma.horario_fim}) - ${turma.vagas_disponiveis} vagas`;
                turmasField.appendChild(option);
                
                // Adiciona o card da turma
                const turmaCard = document.createElement('div');
                turmaCard.className = 'col-md-4 mb-3';
                turmaCard.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${turma.nome}</h5>
                            <p class="card-text">
                                <strong>Dia:</strong> ${turma.dia_semana}<br>
                                <strong>Horário:</strong> ${turma.horario_inicio} - ${turma.horario_fim}<br>
                                <strong>Vagas disponíveis:</strong> ${turma.vagas_disponiveis}
                            </p>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="turmas" value="${turma.id}" id="turma_${turma.id}">
                                <label class="form-check-label" for="turma_${turma.id}">
                                    Selecionar turma
                                </label>
                            </div>
                        </div>
                    </div>
                `;
                turmasContainer.appendChild(turmaCard);
            });
            
            // Habilita o campo de turmas
            turmasField.disabled = false;
        });
}

// Adiciona eventos aos checkboxes de cursos
document.addEventListener('DOMContentLoaded', function() {
    const cursoCheckboxes = document.querySelectorAll('input[name="cursos"]');
    cursoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                loadTurmas(this.value);
            }
        });
    });
});

// Adiciona eventos de clique nos cards dos cursos
document.addEventListener('DOMContentLoaded', function() {
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            openGallery(courseId);
        });
    });
}); 