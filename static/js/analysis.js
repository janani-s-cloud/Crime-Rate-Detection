document.addEventListener('DOMContentLoaded', function () {
    let crimeChart;
    const stateSelect = document.getElementById('stateSelect');
    const districtSelect = document.getElementById('districtSelect');
    const crimeTypeSelect = document.getElementById('crimeTypeSelect');
    const applyBtn = document.getElementById('applyFilters');

    // Initialize Chart
    function initChart() {
        const ctx = document.getElementById('crimeChart').getContext('2d');
        crimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Historical Data',
                        data: [],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#e74c3c',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Projected Trend (to 2025)',
                        data: [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#3498db',
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { title: { display: true, text: 'Year' }, grid: { display: false } },
                    y: { title: { display: true, text: 'Count' }, beginAtZero: false }
                },
                interaction: { mode: 'nearest', axis: 'x', intersect: false }
            }
        });
    }

    // Update Chart with Data
    function updateChart(data, label) {
        crimeChart.data.labels = data.labels;

        // Historical
        crimeChart.data.datasets[0].data = data.historical;
        crimeChart.data.datasets[0].label = `${label} - Historical`;

        // Projected
        crimeChart.data.datasets[1].data = data.projected;

        crimeChart.update();
    }

    // Fetch and Load Data
    function fetchData() {
        const state = stateSelect.value;
        const district = districtSelect.value;
        const crimeType = crimeTypeSelect.value;

        let url = `/api/crime_data?crime_type=${encodeURIComponent(crimeType)}`;
        if (state) url += `&state=${encodeURIComponent(state)}`;
        if (district) url += `&district=${encodeURIComponent(district)}`;

        // Update styling based on crimeType only (optional, keep it simple for now)
        const labelText = state || district ? `${crimeType} (${district || state})` : `${crimeType} (Pan India)`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                updateChart(data, labelText);
            })
            .catch(err => console.error("Error fetching data:", err));
    }

    // Helper: Populate Select Options
    function populateSelect(select, options) {
        // Keep the first option (placeholder)
        const firstOption = select.options[0];
        select.innerHTML = '';
        select.appendChild(firstOption);

        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            select.appendChild(option);
        });
    }

    // Loading Initial Data for Dropdowns
    function loadDropdowns() {
        // Load States
        fetch('/api/states')
            .then(res => res.json())
            .then(data => populateSelect(stateSelect, data));

        // Load Crime Types
        fetch('/api/crime_types')
            .then(res => res.json())
            .then(data => populateSelect(crimeTypeSelect, data));
    }

    // Event Listeners
    stateSelect.addEventListener('change', function () {
        const state = this.value;
        if (state) {
            districtSelect.disabled = false;
            fetch(`/api/districts?state=${encodeURIComponent(state)}`)
                .then(res => res.json())
                .then(data => populateSelect(districtSelect, data));
        } else {
            districtSelect.disabled = true;
            districtSelect.value = "";
        }
    });

    applyBtn.addEventListener('click', fetchData);

    // Initial Setup
    initChart();
    loadDropdowns();
    fetchData(); // Load default data
});
