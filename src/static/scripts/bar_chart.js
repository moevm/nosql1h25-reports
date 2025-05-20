$(document).ready(function () {
    function transformChartData(datasetsRaw) {
        if (datasetsRaw === {}) {
            return null;
        }

        const rawLabels = datasetsRaw.data_labels;
        const rawData = datasetsRaw.data;

        const datasets = rawLabels.map((label, index) => {
            return {
                label: label,
                data: rawData[index],
            };
        });

        return {
            title: datasetsRaw.title,
            labels: datasetsRaw.labels,
            datasets: datasets
        };
    }

    const data = transformChartData(rawData);
    const ctx = document.getElementById('barChart');

    if (data !== null) {
        $('.stackedBarChart').css('background-color', 'white');

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: data.title
                    },
                    colors: {
                        forceOverride: true
                    },
                    customCanvasBackgroundColor: {
                        color: 'white',
                    }
                },
                responsive: true,
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true
                    }
                }
            }
        });
    } else {
        $('.stackedBarChart').css('background-color', '');
    }
});