document.addEventListener("DOMContentLoaded", function () {
    // Função para mudar a imagem principal
    let currentIndex = {};  // Objeto para armazenar os índices de cada curso

    function changeImage(direction, courseId) {
        const images = document.querySelectorAll(`#${courseId}-gallery .gallery-item`);
        if (typeof direction === "number") {
            currentIndex[courseId] = direction;  // Atualiza o índice para o curso específico
        } else {
            currentIndex[courseId] = (currentIndex[courseId] + direction + images.length) % images.length;
        }

        const mainImage = document.getElementById(`mainImage-${courseId}`);
        mainImage.src = images[currentIndex[courseId]].src;  // Atualiza a imagem principal
    }

    // Função para abrir a galeria
    function openGallery(courseId) {
        const gallery = document.getElementById(`${courseId}-gallery`);
        gallery.style.display = "block";  // Exibe a galeria
    }

    // Função para fechar a galeria
    function closeGallery(courseId) {
        const gallery = document.getElementById(`${courseId}-gallery`);
        gallery.style.display = "none";  // Esconde a galeria
    }

    // Adiciona evento de clique aos cards de curso
    let courseCards = document.querySelectorAll(".course-card");

    courseCards.forEach(card => {
        card.addEventListener("click", function () {
            let courseId = this.getAttribute("data-course-id");
            openGallery(courseId);  // Abre a galeria quando o card for clicado
        });
    });

    // Fecha a galeria ao clicar fora dela
    document.addEventListener("click", function (event) {
        const gallery = document.querySelector(".gallery-container");
        if (gallery && !gallery.contains(event.target) && !event.target.closest(".course-card")) {
            gallery.style.display = "none";  // Fecha a galeria se clicar fora
        }
    });

    // Evento para o botão de fechar galeria
    let closeButtons = document.querySelectorAll(".close-gallery");
    closeButtons.forEach(button => {
        button.addEventListener("click", function () {
            let courseId = this.closest('.gallery-container').id.replace("-gallery", "");
            closeGallery(courseId);  // Fecha a galeria ao clicar no botão de fechar
        });
    });

    // Eventos para navegação com as setas
    const courses = document.querySelectorAll(".course-card");

    courses.forEach(course => {
        const courseId = course.getAttribute("data-course-id");

        // Clique nas miniaturas da galeria para mudar a imagem
        const galleryImages = document.querySelectorAll(`#${courseId}-gallery .gallery-item`);
        galleryImages.forEach((image, index) => {
            image.addEventListener("click", function() {
                changeImage(index, courseId);  // Muda para a imagem clicada
            });
        });
    });
});
