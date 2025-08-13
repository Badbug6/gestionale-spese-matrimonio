document.addEventListener('DOMContentLoaded', function () {
    const categoryCanvas = document.getElementById('category-chart');
    const paymentsCanvas = document.getElementById('payments-over-time-chart');
    if (!categoryCanvas || !paymentsCanvas) return;

    // --- Inizializzazione Grafici ---
    const chartColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#E7E9ED', '#8D3F97', '#7E57C2', '#EA80FC'];
    let categoryChart = new Chart(categoryCanvas, {
        type: 'pie', data: { labels: [], datasets: [{ data: [], backgroundColor: chartColors }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { color: '#fff' } } } }
    });
    let paymentsOverTimeChart = new Chart(paymentsCanvas, {
        type: 'line', data: { labels: [], datasets: [{ label: 'Totale Pagato', data: [], fill: true, backgroundColor: 'rgba(231, 60, 126, 0.2)', borderColor: 'rgba(231, 60, 126, 1)', tension: 0.3 }] },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, ticks: { color: 'rgba(255, 255, 255, 0.7)' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, x: { ticks: { color: 'rgba(255, 255, 255, 0.7)' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } } },
            plugins: { legend: { display: false } }
        }
    });

    // --- Logica per lo Switch dei Grafici ---
    const btnPieChart = document.getElementById('btn-pie-chart');
    const btnLineChart = document.getElementById('btn-line-chart');
    const chartTitle = document.getElementById('chart-title');

    btnPieChart.addEventListener('click', () => {
        chartTitle.textContent = 'Spese per Categoria';
        categoryCanvas.style.display = 'block';
        paymentsCanvas.style.display = 'none';
        btnPieChart.classList.add('active');
        btnLineChart.classList.remove('active');
    });

    btnLineChart.addEventListener('click', () => {
        chartTitle.textContent = 'Andamento Pagamenti Mensili';
        categoryCanvas.style.display = 'none';
        paymentsCanvas.style.display = 'block';
        btnPieChart.classList.remove('active');
        btnLineChart.classList.add('active');
    });

    // --- Funzioni di Aggiornamento UI ---
    function updateUI(state) {
        // Aggiorna sempre entrambi i grafici, anche se uno è nascosto
        categoryChart.data.labels = Object.keys(state.spese_per_categoria);
        categoryChart.data.datasets[0].data = Object.values(state.spese_per_categoria);
        categoryChart.update();

        paymentsOverTimeChart.data.labels = state.pagamenti_mensili.labels;
        paymentsOverTimeChart.data.datasets[0].data = state.pagamenti_mensili.data;
        paymentsOverTimeChart.update();
        
        updateTable(state.spese);
        updateSummaryCards(state);
    }
    
    function updateTable(spese) {
        const tableBody = document.getElementById('spese-table-body');
        tableBody.innerHTML = '';
        spese.forEach(spesa => {
            tableBody.innerHTML += `
                <tr id="spesa-${spesa.id}">
                    <td><a href="/edit/${spesa.id}">${spesa.descrizione}</a></td>
                    <td>€ ${parseFloat(spesa.importo).toFixed(2)}</td>
                    <td>€ ${parseFloat(spesa.totale_pagato).toFixed(2)}</td>
                    <td>${spesa.categoria}</td>
                    <td>${spesa.username || 'N/D'}</td>
                    <td class="action-buttons"><button class="delete-btn" onclick="deleteExpense(${spesa.id})">Elimina</button></td>
                </tr>`;
        });
    }
    
    function updateSummaryCards(state) {
        document.querySelector('.summary-cards .card:nth-child(1) p').textContent = `€ ${parseFloat(state.budget_totale).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(2) p').textContent = `€ ${parseFloat(state.speso_totale_previsto).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(3) p').textContent = `€ ${parseFloat(state.speso_totale_effettivo).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(4) p').textContent = `€ ${parseFloat(state.rimanente_previsto).toFixed(2)}`;
    }

    // --- Inizializzazione e Gestione Form ---
    const expenseForm = document.getElementById('expense-form');
    expenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            descrizione: document.getElementById('form-descrizione').value,
            importo: document.getElementById('form-importo').value,
            categoria: document.getElementById('form-categoria').value,
        };
        const response = await fetch('/api/add_expense', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (response.ok) {
            updateUI(await response.json());
            expenseForm.reset();
        } else {
            alert(`Errore: ${(await response.json()).error}`);
        }
    });
    
    if (typeof initialState !== 'undefined') {
        updateUI(initialState);
    }
});

async function deleteExpense(id) {
    if (!confirm('Sei sicuro di voler eliminare questa spesa?')) return;
    const response = await fetch(`/api/delete_expense/${id}`, { method: 'POST' });
    if (response.ok) {
        document.getElementById('spese-table-body').innerHTML = ''; // Svuota e lascia che updateUI ricostruisca
        // Richiamare la funzione di aggiornamento UI definita nel blocco DOMContentLoaded
        // Poiché non possiamo accedervi direttamente, potremmo dover ricaricare i dati o ristrutturare leggermente il codice.
        // Per semplicità, in questo caso, ricarichiamo la pagina per vedere le modifiche.
        location.reload(); 
    } else {
        alert(`Errore: ${(await response.json()).error}`);
    }
}