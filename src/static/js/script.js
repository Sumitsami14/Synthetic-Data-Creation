document.addEventListener('DOMContentLoaded', () => {
    // === Navigation ===
    const navBtns = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.view-section');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update Nav
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update View
            const viewId = `view-${btn.dataset.view}`;
            sections.forEach(s => {
                s.classList.remove('active');
                if (s.id === viewId) s.classList.add('active');
            });

            // Refresh Dashboard if selecting dashboard
            if (btn.dataset.view === 'dashboard') {
                loadDashboardData();
            }
        });
    });

    // === Dashboard Logic ===
    let statusChart = null;

    async function loadDashboardData() {
        try {
            // 1. Fetch Summary Stats
            const statsRes = await fetch('/api/stats');
            const stats = await statsRes.json();

            document.getElementById('stat-total-req').textContent = stats.total_requests;
            document.getElementById('stat-completed').textContent = stats.completed_requests;
            document.getElementById('stat-customers').textContent = stats.total_customers_generated;

            // 2. Render/Update Chart
            renderChart(stats);

            // 3. Fetch History Table
            loadHistoryTable();

        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    function renderChart(stats) {
        const ctx = document.getElementById('statusChart').getContext('2d');
        const data = {
            labels: ['Completed', 'Failed', 'Processing/Queued'],
            datasets: [{
                data: [
                    stats.completed_requests,
                    stats.failed_requests,
                    stats.total_requests - (stats.completed_requests + stats.failed_requests)
                ],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 0
            }]
        };

        if (statusChart) {
            statusChart.data = data;
            statusChart.update();
        } else {
            statusChart = new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options: {
                    responsive: true,
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        }
    }

    async function loadHistoryTable() {
        const res = await fetch('/api/history');
        const logs = await res.json();
        const tbody = document.getElementById('dashboard-history-body');

        tbody.innerHTML = logs.slice(0, 5).map(log => `
            <tr>
                <td>#${log.id}</td>
                <td>${new Date(log.timestamp).toLocaleDateString()}</td>
                <td>${log.customers_count} Records</td>
                <td>
                    <span style="color: ${getStatusColor(log.status)}">
                        ${log.status}
                    </span>
                </td>
            </tr>
        `).join('');
    }

    function getStatusColor(status) {
        if (status === 'Completed') return '#10b981';
        if (status === 'Failed') return '#ef4444';
        return '#f59e0b';
    }

    document.getElementById('refreshStats').addEventListener('click', loadDashboardData);

    // Initial Load
    loadDashboardData();


    // === Generator Logic (Legacy) ===
    const generateForm = document.getElementById('generateForm');
    if (generateForm) {
        generateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('generateBtn');
            const textSpan = btn.querySelector('span');
            const spinner = btn.querySelector('.spinner');

            // UI Loading State
            textSpan.textContent = "Processing...";
            // spinner.style.display = 'block'; // Ensure your CSS handles this or just text change
            btn.disabled = true;

            const customers = document.getElementById('customers').value;
            const format = document.getElementById('format').value;

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ customers: parseInt(customers), format })
                });

                if (res.ok) {
                    alert('Generation started! Check the dashboard for progress.');
                    generateForm.reset();
                    // Switch to dashboard
                    document.querySelector('[data-view="dashboard"]').click();
                } else {
                    alert('Failed to start generation.');
                }
            } catch (err) {
                console.error(err);
                alert('Error connecting to server.');
            } finally {
                textSpan.textContent = "Start Generation";
                btn.disabled = false;
            }
        });
    }

    // === Agent Chat Logic ===
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatHistory = document.getElementById('chatHistory');

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add User Message
        appendMessage('user', text);
        chatInput.value = '';

        // Typing indicator could go here

        try {
            const res = await fetch('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            // Add Agent Response
            appendMessage('system', data.response);

            if (data.job_id) {
                appendMessage('system', `Job ID: ${data.job_id} started. Check the Dashboard.`);
            }
        } catch (err) {
            appendMessage('system', "Sorry, I encountered an error processing your request.");
            console.error(err);
        }
    }

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i></div>
            <div class="content"><p>${text}</p></div>
        `;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    sendChatBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

});
