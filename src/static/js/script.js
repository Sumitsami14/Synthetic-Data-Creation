document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generateForm');
    const tableBody = document.getElementById('historyTableBody');
    const refreshBtn = document.getElementById('refreshBtn');

    // Load history on start
    fetchHistory();

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const customers = document.getElementById('customers').value;
        const format = document.getElementById('format').value;
        const btn = document.getElementById('generateBtn');

        btn.disabled = true;
        btn.innerText = 'Starting...';

        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customers: parseInt(customers),
                    format
                })
            });

            if (res.ok) {
                // Refresh table immediately to show queued job
                fetchHistory();
            } else {
                alert("Failed to start generation");
            }
        } catch (err) {
            console.error(err);
            alert("Error sending request");
        } finally {
            btn.disabled = false;
            btn.innerText = 'Start Generation';
        }
    });

    // Refresh Button
    refreshBtn.addEventListener('click', fetchHistory);

    // Poll for updates every 5 seconds
    setInterval(fetchHistory, 5000);

    async function fetchHistory() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            renderTable(data);
        } catch (err) {
            console.error("Failed to fetch history", err);
        }
    }

    function renderTable(data) {
        tableBody.innerHTML = '';

        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: #64748b;">No requests yet.</td></tr>';
            return;
        }

        data.forEach(row => {
            const date = new Date(row.timestamp).toLocaleString();
            let actionHtml = '-';

            if (row.status === 'Completed' && row.file_path) {
                actionHtml = `<a href="/api/download/${row.id}" class="download-link">Download ZIP</a>`;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${row.id}</td>
                <td>${date}</td>
                <td>${row.customers_count}</td>
                <td><span class="status-badge status-${row.status}">${row.status}</span></td>
                <td>${actionHtml}</td>
            `;
            tableBody.appendChild(tr);
        });
    }
});
