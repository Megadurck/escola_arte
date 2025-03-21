document.addEventListener("DOMContentLoaded", function() {
    // Variáveis globais para armazenar instâncias dos gráficos
    let barChartInstance = null;
    let pieChartInstance = null;

    fetch('/inscricoes/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            const cursos = data.inscricoes_por_curso.map(item => item.curso);
            const totais = data.inscricoes_por_curso.map(item => item.total);
            const porcentagens = data.inscricoes_por_curso.map(item => item.porcentagem);

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
                barChartInstance.destroy();  // Destruir gráfico existente
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
                    maintainAspectRatio: false, // O gráfico já é responsivo
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
                pieChartInstance.destroy();  // Destruir gráfico existente
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
                    maintainAspectRatio: false, // O gráfico já é responsivo
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
        })
        .catch(error => {
            console.error('Erro ao buscar dados para os gráficos:', error);
        });
});
