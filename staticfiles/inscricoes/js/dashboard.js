document.addEventListener("DOMContentLoaded", function() {
    let barChartInstance = null;
    let pieChartInstance = null;
    let lineChartInstance = null;

    // Buscar os dados da API
    fetch('/inscricoes/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            console.log("Dados recebidos:", data);  // Verifique todos os dados recebidos

            if (!data || !data.inscricoes_por_curso || !data.data_inscricao) {
                console.error("Dados inválidos recebidos.");
                return;
            }

            // Mapear os dados para os gráficos
            const cursos = data.inscricoes_por_curso.map(item => item.curso);
            const totais = data.inscricoes_por_curso.map(item => item.total);
            const porcentagens = data.inscricoes_por_curso.map(item => item.porcentagem);
            const datas = data.data_inscricao.map(item => item.data_inscricao ? new Date(item.data_inscricao).toLocaleDateString() : ''); // lista de datas
            const quantidades = data.data_inscricao.map(item => item.count || 0); // Adicionado para verificar as quantidades

            // Verifique as variáveis para garantir que estão corretas
            console.log("Cursos:", cursos);
            console.log("Totais:", totais);
            console.log("Porcentagens:", porcentagens);

            console.log("Datas (formato Date):", datas);
            console.log("Quantidades:", quantidades); // Adicionado para verificar as quantidades

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
        });
});

