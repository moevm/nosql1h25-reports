const ctx = document.getElementById('barChart');


new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
        plugins: {
            title: {
                display: true,
                text: data.title
            },
            colors: {
                forceOverride: true
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

