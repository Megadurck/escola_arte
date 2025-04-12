// Funções para a galeria de imagens
function openGallery(courseId) {
    const gallery = document.getElementById(`${courseId}-gallery`);
    if (gallery) {
        gallery.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Previne rolagem do body
    }
}

function closeGallery(courseId) {
    const gallery = document.getElementById(`${courseId}-gallery`);
    if (gallery) {
        gallery.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaura rolagem do body
    }
}

function changeImage(index, courseId) {
    const mainImage = document.getElementById(`mainImage-${courseId}`);
    const galleryItems = document.querySelectorAll(`#${courseId}-gallery .gallery-item`);
    
    if (mainImage && galleryItems[index]) {
        mainImage.src = galleryItems[index].src;
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
    // Adiciona event listeners para todos os cards de curso
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            if (courseId) {
                openGallery(courseId);
            }
        });
    });
}); 