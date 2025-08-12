document.addEventListener('DOMContentLoaded', function () {
    // --- GRAFICO A TORTA CON CHART.JS ---
    const ctx = document.getElementById('category-chart');
    if (!ctx) return; // Non eseguire se non siamo nella pagina giusta

    // Colori personalizzati per il grafico
    const chartColors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#E7E9ED', '#8D3F97', '#7E57C2', '#EA80FC'
    ];

    let categoryChart = new Chart(ctx, {
        type: 'pie', // o 'doughnut' per il grafico a ciambella
        data: {
            labels: [], // Verranno riempiti dinamicamente
            datasets: [{
                label: 'Spese',
                data: [], // Verranno riempiti dinamicamente
                backgroundColor: chartColors,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#fff' // Colore del testo della legenda
                    }
                }
            }
        }
    });

    // --- FUNZIONI PER AGGIORNARE LA UI ---
    function updateUI(state) {
        updateChart(state.spese_per_categoria);
        updateTable(state.spese);
        updateSummaryCards(state);
    }
    
    function updateChart(spesePerCategoria) {
        const labels = Object.keys(spesePerCategoria);
        const data = Object.values(spesePerCategoria);
        
        categoryChart.data.labels = labels;
        categoryChart.data.datasets[0].data = data;
        categoryChart.update();
    }

    function updateTable(spese) {
        const tableBody = document.getElementById('spese-table-body');
        if (!tableBody) return;
        tableBody.innerHTML = ''; // Svuota la tabella attuale

        spese.forEach(spesa => {
            const row = `
                <tr id="spesa-${spesa.id}">
                    <td><a href="/spesa/${spesa.id}">${spesa.descrizione}</a></td>
                    <td>€ ${parseFloat(spesa.importo).toFixed(2)}</td>
                    <td>€ ${parseFloat(spesa.totale_pagato).toFixed(2)}</td>
                    <td>${spesa.categoria}</td>
                    <td>${spesa.username || 'N/D'}</td>
                    <td class="action-buttons">
                        <a href="/edit/${spesa.id}" class="edit-btn">Modifica</a>
                        <button class="delete-btn" onclick="deleteExpense(${spesa.id})">Elimina</button>
                    </td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    }
    
    function updateSummaryCards(state) {
        document.querySelector('.summary-cards .card:nth-child(1) p').textContent = `€ ${parseFloat(state.budget_totale).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(2) p').textContent = `€ ${parseFloat(state.speso_totale_previsto).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(3) p').textContent = `€ ${parseFloat(state.speso_totale_effettivo).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(4) p').textContent = `€ ${parseFloat(state.rimanente_previsto).toFixed(2)}`;
    }

    // --- GESTIONE FORM AGGIUNGI SPESA ---
    const expenseForm = document.getElementById('expense-form');
    if (expenseForm) {
        expenseForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            
            const descrizione = document.getElementById('form-descrizione').value;
            const importo = document.getElementById('form-importo').value;
            const categoria = document.getElementById('form-categoria').value;

            if (!descrizione || !importo || !categoria) {
                alert('Tutti i campi sono obbligatori!');
                return;
            }

            const response = await fetch('/api/add_expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ descrizione, importo, categoria })
            });

            if (response.ok) {
                const newState = await response.json();
                updateUI(newState);
                expenseForm.reset(); // Pulisce il form
            } else {
                const error = await response.json();
                alert(`Errore: ${error.error}`);
            }
        });
    }
    
    // Inizializza la UI con i dati passati dal server
    if (typeof initialState !== 'undefined') {
        updateUI(initialState);
    }
});

// --- FUNZIONE PER ELIMINARE UNA SPESA ---
// La definiamo fuori dall'evento DOMContentLoaded per renderla globale
async function deleteExpense(id) {
    if (!confirm('Sei sicuro di voler eliminare questa spesa?')) {
        return;
    }

    const response = await fetch(`/api/delete_expense/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        const newState = await response.json();
        // Richiamiamo le funzioni di aggiornamento
        document.getElementById(`spesa-${id}`).remove(); // Rimuove la riga dalla tabella per un feedback immediato
        
        // Ricostruiamo la UI con i dati aggiornati
        const chartCtx = document.getElementById('category-chart').getContext('2d');
        let chart = Chart.getChart(chartCtx); // Recupera l'istanza del grafico
        
        const labels = Object.keys(newState.spese_per_categoria);
        const data = Object.values(newState.spese_per_categoria);
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();

        document.querySelector('.summary-cards .card:nth-child(1) p').textContent = `€ ${parseFloat(newState.budget_totale).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(2) p').textContent = `€ ${parseFloat(newState.speso_totale_previsto).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(3) p').textContent = `€ ${parseFloat(newState.speso_totale_effettivo).toFixed(2)}`;
        document.querySelector('.summary-cards .card:nth-child(4) p').textContent = `€ ${parseFloat(newState.rimanente_previsto).toFixed(2)}`;

    } else {
        const error = await response.json();
        alert(`Errore: ${error.error}`);
    }
}