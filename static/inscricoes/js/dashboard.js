document.addEventListener("DOMContentLoaded", function() {
    console.log("Iniciando carregamento do dashboard...");
    
    // Verificar se Chart.js está disponível
    if (typeof Chart === 'undefined') {
        console.error('Chart.js não está carregado. Por favor, inclua a biblioteca Chart.js antes de usar este script.');
        return;
    }
    console.log("Chart.js está disponível", Chart.version);

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

    console.log("Verificando elementos do DOM:", {
        barChart: barChartElement ? "Encontrado" : "Não encontrado",
        pieChart: pieChartElement ? "Encontrado" : "Não encontrado",
        lineChart: lineChartElement ? "Encontrado" : "Não encontrado"
    });

    if (!barChartElement || !pieChartElement || !lineChartElement) {
        console.error('Elementos necessários para os gráficos não foram encontrados:', {
            barChart: !!barChartElement,
            pieChart: !!pieChartElement,
            lineChart: !!lineChartElement
        });
        return;
    }
    console.log("Elementos do DOM encontrados com sucesso");

    // Função para criar gráfico de barras
    function createBarChart(data) {
        console.log("Criando gráfico de barras com dados:", data);
        if (barChartInstance) {
            console.log("Destruindo instância anterior do gráfico de barras");
            barChartInstance.destroy();
        }
        try {
            barChartInstance = new Chart(barChartElement, {
                type: 'bar',
                data: {
                    labels: data.cursos,
                    datasets: [{
                        label: 'Total de Inscrições',
                        data: data.totais,
                        backgroundColor: data.backgroundColors,
                        borderColor: data.backgroundColors.map(color => color.replace('0.5', '1')),
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
            console.log("Gráfico de barras criado com sucesso");
        } catch (error) {
            console.error("Erro ao criar gráfico de barras:", error);
            throw error;
        }
    }

    // Função para criar gráfico de pizza
    function createPieChart(data) {
        console.log("Criando gráfico de pizza com dados:", data);
        if (pieChartInstance) {
            console.log("Destruindo instância anterior do gráfico de pizza");
            pieChartInstance.destroy();
        }
        try {
            pieChartInstance = new Chart(pieChartElement, {
                type: 'pie',
                data: {
                    labels: data.cursos,
                    datasets: [{
                        label: 'Porcentagem de Inscrições',
                        data: data.porcentagens,
                        backgroundColor: data.backgroundColors,
                        borderColor: data.backgroundColors.map(color => color.replace('0.5', '1')),
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
            console.log("Gráfico de pizza criado com sucesso");
        } catch (error) {
            console.error("Erro ao criar gráfico de pizza:", error);
            throw error;
        }
    }

    // Função para criar gráfico de linha
    function createLineChart(data) {
        console.log("Criando gráfico de linha com dados:", data);
        if (lineChartInstance) {
            console.log("Destruindo instância anterior do gráfico de linha");
            lineChartInstance.destroy();
        }
        try {
            lineChartInstance = new Chart(lineChartElement, {
                type: 'line',
                data: {
                    labels: data.datas,
                    datasets: [{
                        label: 'Inscrições ao Longo do Tempo',
                        data: data.quantidades,
                        fill: true,
                        borderColor: 'rgb(2, 19, 19)',
                        backgroundColor: 'rgba(2, 19, 19, 0.2)',
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 8,
                        showLine: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true },
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
                                text: 'Número de Inscrições'
                            }
                        }
                    }
                }
            });
            console.log("Gráfico de linha criado com sucesso");
        } catch (error) {
            console.error("Erro ao criar gráfico de linha:", error);
            throw error;
        }
    }

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

        // Criar os gráficos
        try {
            createBarChart({ cursos, totais, backgroundColors });
            createPieChart({ cursos, porcentagens, backgroundColors });
            createLineChart({ datas, quantidades });
            console.log("Todos os gráficos foram criados com sucesso");
        } catch (error) {
            console.error("Erro ao criar os gráficos:", error);
            throw error;
        }
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

