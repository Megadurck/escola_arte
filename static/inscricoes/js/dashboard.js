document.addEventListener("DOMContentLoaded", function() {
    console.log("Iniciando carregamento do dashboard...");
    
    // Verificar se Chart.js está disponível
    if (typeof Chart === 'undefined') {
        console.error('Chart.js não está carregado. Por favor, inclua a biblioteca Chart.js antes de usar este script.');
        return;
    }
    console.log("Chart.js está disponível");

    let barChartInstance = null;
    let pieChartInstance = null;
    let lineChartInstance = null;

    // Função para limpar os gráficos
    function cleanupCharts() {
        if (barChartInstance) barChartInstance.destroy();
        if (pieChartInstance) pieChartInstance.destroy();
        if (lineChartInstance) lineChartInstance.destroy();
    }

    // Limpar gráficos quando a página for fechada
    window.addEventListener('beforeunload', cleanupCharts);

    // Verificar se os elementos do DOM existem
    const barChartElement = document.getElementById('barChart');
    const pieChartElement = document.getElementById('pieChart');
    const lineChartElement = document.getElementById('lineChart');

    if (!barChartElement || !pieChartElement || !lineChartElement) {
        console.error('Elementos necessários para os gráficos não foram encontrados:', {
            barChart: !!barChartElement,
            pieChart: !!pieChartElement,
            lineChart: !!lineChartElement
        });
        return;
    }
    console.log("Elementos do DOM encontrados com sucesso");

    // Buscar os dados da API
    console.log("Iniciando requisição para /inscricoes/dashboard-data/");
    fetch('/inscricoes/dashboard-data/', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log("Status da resposta:", response.status);
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Acesso não autorizado. Você precisa estar logado como administrador.');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Dados recebidos:", data);

        // Validação mais robusta dos dados
        if (!data || !Array.isArray(data.inscricoes_por_curso) || !Array.isArray(data.data_inscricao)) {
            throw new Error('Formato de dados inválido');
        }

        if (data.inscricoes_por_curso.length === 0 || data.data_inscricao.length === 0) {
            throw new Error('Não há dados para exibir');
        }

        // Mapear os dados para os gráficos com validação
        const cursos = data.inscricoes_por_curso.map(item => {
            if (!item || typeof item.curso !== 'string') {
                throw new Error('Dados de curso inválidos');
            }
            return item.curso;
        });

        const totais = data.inscricoes_por_curso.map(item => {
            if (typeof item.total !== 'number') {
                throw new Error('Dados de totais inválidos');
            }
            return item.total;
        });

        const porcentagens = data.inscricoes_por_curso.map(item => {
            if (typeof item.porcentagem !== 'number') {
                throw new Error('Dados de porcentagens inválidos');
            }
            return item.porcentagem;
        });

        const datas = data.data_inscricao.map(item => {
            if (!item.data_inscricao) return '';
            const date = new Date(item.data_inscricao);
            return isNaN(date.getTime()) ? '' : date.toLocaleDateString();
        }).filter(date => date !== '');

        const quantidades = data.data_inscricao.map(item => {
            if (typeof item.count !== 'number') {
                throw new Error('Dados de quantidades inválidos');
            }
            return item.count;
        });

        console.log("Dados processados:", {
            cursos,
            totais,
            porcentagens,
            datas,
            quantidades
        });

        const backgroundColors = [
            'rgba(23, 213, 197, 0.5)',
            'rgba(20, 241, 61, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(30, 166, 219, 0.5)',
            'rgba(25, 5, 66, 0.5)',
            'rgba(247, 132, 0, 0.5)',
            'rgba(171, 230, 9, 0.5)',
            'rgba(136, 19, 232, 0.5)',
        ];

        // Gráfico de Barras
        if (barChartInstance) {
            barChartInstance.destroy();
        }
        barChartInstance = new Chart(document.getElementById('barChart'), {
            type: 'bar',
            data: {
                labels: cursos,
                datasets: [{
                    label: 'Total de Inscrições',
                    data: totais,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.5', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: ctx => `${ctx.raw} inscrições`
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // Gráfico de Pizza
        if (pieChartInstance) {
            pieChartInstance.destroy();
        }
        pieChartInstance = new Chart(document.getElementById('pieChart'), {
            type: 'pie',
            data: {
                labels: cursos,
                datasets: [{
                    label: 'Porcentagem de Inscrições',
                    data: porcentagens,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('0.5', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: ctx => `${ctx.raw.toFixed(0)}% das inscrições`
                        }
                    }
                }
            }
        });

        // Gráfico de Linha (com datas)
        if (lineChartInstance) {
            lineChartInstance.destroy();
        }
        lineChartInstance = new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels: datas,
                datasets: [{
                    label: 'Inscrições ao Longo do Tempo',
                    data: quantidades,
                    fill: true,
                    borderColor: 'rgb(2, 19, 19)',
                    backgroundColor: 'rgba(2, 19, 19, 0.2)', // Adiciona uma cor de fundo ao gráfico de linha
                    tension: 0.4, // Aumenta a tensão para suavizar as curvas
                    pointRadius: 3,
                    pointHoverRadius: 8,
                    showLine: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }, // Adiciona uma legenda ao gráfico
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: ctx => `${ctx.raw} inscrições`
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        title: {
                            display: true,
                            text: 'Data'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de Inscrições' // Adiciona título ao eixo Y
                        }
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Erro ao buscar dados para os gráficos:', error);
        // Adicionar mensagem de erro na interface
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger';
        errorMessage.textContent = `Erro ao carregar os dados do dashboard: ${error.message}`;
        document.querySelector('.container').prepend(errorMessage);
    });
});

