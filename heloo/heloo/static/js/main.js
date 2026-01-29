// Expense Tracker Multi-Page Application
const API_BASE_URL = '/api';
let currentPage = 'dashboard';
let charts = {};

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Switch between pages
function switchPage(page) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(el => el.classList.add('hidden'));

    // Show selected page
    const selectedPage = document.getElementById(`${page}-page`);
    if (selectedPage) {
        selectedPage.classList.remove('hidden');
    }

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-page="${page}"]`).classList.add('active');

    currentPage = page;

    // Load page data
    if (page === 'dashboard') loadDashboard();
    if (page === 'expenses') loadExpenses();
    if (page === 'analytics') loadAnalytics();
    if (page === 'budgets') loadBudgets();
    if (page === 'goals') loadGoals();
    if (page === 'settings') loadSettings();
}

// ===== DASHBOARD =====
async function loadDashboard() {
    const [expenses, budgets] = await Promise.all([
        fetch(`${API_BASE_URL}/expenses/`).then(r => r.json()),
        fetch(`${API_BASE_URL}/budget-status/`).then(r => r.json())
    ]);

    // Update stats
    const total = expenses.reduce((sum, exp) => sum + exp.amount, 0);
    const count = expenses.length;
    const average = count > 0 ? (total / count) : 0;

    // This month
    const now = new Date();
    const thisMonth = expenses.filter(exp => {
        const expDate = new Date(exp.date);
        return expDate.getMonth() === now.getMonth() && expDate.getFullYear() === now.getFullYear();
    }).reduce((sum, exp) => sum + exp.amount, 0);

    document.getElementById('dashTotal').textContent = `₹${total.toFixed(2)}`;
    document.getElementById('dashCount').textContent = count;
    document.getElementById('dashAverage').textContent = `₹${average.toFixed(2)}`;
    document.getElementById('dashMonth').textContent = `₹${thisMonth.toFixed(2)}`;

    // Recent expenses
    const recent = expenses.slice(-5).reverse();
    let recentHTML = '';
    recent.forEach(exp => {
        recentHTML += `
            <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-all duration-300 hover:shadow-lg">
                <div class="flex justify-between items-center">
                    <div>
                        <p class="font-semibold text-slate-100">${exp.category}</p>
                        <p class="text-slate-400 text-sm">${new Date(exp.date).toLocaleDateString()}</p>
                    </div>
                    <p class="text-xl font-bold text-blue-400">₹${exp.amount.toFixed(2)}</p>
                </div>
            </div>
        `;
    });
    document.getElementById('dashRecentExpenses').innerHTML = recentHTML || '<p class="text-slate-500">No expenses yet</p>';

    // Budget status
    let budgetHTML = '';
    budgets.forEach(budget => {
        const color = budget.is_exceeded ? 'red' : budget.percentage > 80 ? 'yellow' : 'green';
        budgetHTML += `
            <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-all duration-300 hover:shadow-lg">
                <div class="flex justify-between items-center mb-3">
                    <p class="font-semibold text-slate-100">${budget.category}</p>
                    <p class="text-sm font-bold text-slate-300">${budget.percentage}%</p>
                </div>
                <div class="w-full bg-slate-700 rounded-full h-3">
                    <div class="bg-${color}-500 h-3 rounded-full transition-all duration-300" style="width: ${Math.min(budget.percentage, 100)}%"></div>
                </div>
                <p class="text-xs text-slate-400 mt-3">₹${budget.spent.toFixed(2)} / ₹${budget.limit.toFixed(2)}</p>
            </div>
        `;
    });
    document.getElementById('dashBudgetStatus').innerHTML = budgetHTML || '<p class="text-slate-500">No budgets set</p>';
}

// ===== EXPENSES =====
async function loadExpenses() {
    try {
        const response = await fetch(`${API_BASE_URL}/expenses/`);
        const expenses = await response.json();
        displayExpensesList(expenses);
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

function displayExpensesList(expenses) {
    let html = '';
    const sorted = expenses.sort((a, b) => new Date(b.date) - new Date(a.date));

    sorted.forEach(expense => {
                html += `
            <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6 flex justify-between items-start hover:border-slate-600 hover:shadow-xl transition-all duration-300 group">
                <div class="flex-1">
                    <p class="font-bold text-lg text-slate-100">${expense.category}</p>
                    <p class="text-slate-400 text-sm mt-1">${new Date(expense.date).toLocaleDateString()}</p>
                    ${expense.notes ? `<p class="text-slate-500 text-sm mt-3 italic">"${expense.notes}"</p>` : ''}
                </div>
                <div class="text-right ml-4">
                    <p class="font-bold text-3xl text-blue-400">₹${expense.amount.toFixed(2)}</p>
                    <div class="flex gap-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <button onclick="editExpense(${expense.id})" class="text-xs bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/60 text-blue-300 px-3 py-2 rounded-lg transition-all duration-200 font-medium">Edit</button>
                        <button onclick="deleteExpense(${expense.id})" class="text-xs bg-red-600/30 hover:bg-red-600/50 border border-red-500/60 text-red-300 px-3 py-2 rounded-lg transition-all duration-200 font-medium">Delete</button>
                    </div>
                </div>
            </div>
        `;
    });
    
    document.getElementById('expensesList').innerHTML = html || '<p class="text-slate-500">No expenses found</p>';
}

async function applyFilters() {
    const category = document.getElementById('filterCategory').value;
    const startDate = document.getElementById('filterStartDate').value;
    const endDate = document.getElementById('filterEndDate').value;
    
    let url = `${API_BASE_URL}/expenses/`;
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    if (params.toString()) url += '?' + params.toString();
    
    const response = await fetch(url);
    const expenses = await response.json();
    displayExpensesList(expenses);
}

async function deleteExpense(id) {
    if (!confirm('Delete this expense?')) return;
    
    try {
        await fetch(`${API_BASE_URL}/expenses/${id}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        loadExpenses();
    } catch (error) {
        alert('Error deleting expense');
    }
}

function editExpense(id) {
    alert('Edit feature coming soon!');
}

async function exportData() {
    const response = await fetch(`${API_BASE_URL}/expenses/`);
    const expenses = await response.json();
    
    let csv = 'Date,Category,Amount,Notes\n';
    expenses.forEach(exp => {
        csv += `${new Date(exp.date).toLocaleDateString()},"${exp.category}","${exp.amount}","${exp.notes || ''}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const expenseForm = document.getElementById('expenseForm');
    if (expenseForm) {
        expenseForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;
            const notes = document.getElementById('notes').value;
            const recurring = document.getElementById('recurring').value;
            
            if (!amount || !category) {
                alert('Please fill in all required fields');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/expenses/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        amount: parseFloat(amount),
                        category: category,
                        notes: notes,
                        is_recurring: recurring !== '',
                        recurring_frequency: recurring || null,
                        currency: 'INR'
                    }),
                });
                
                if (response.ok) {
                    expenseForm.reset();
                    loadExpenses();
                    loadDashboard();
                } else {
                    alert('Error adding expense');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error adding expense');
            }
        });
    }
    
    // Budget form
    const budgetForm = document.getElementById('budgetForm');
    if (budgetForm) {
        budgetForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const category = document.getElementById('budgetCategory').value;
            const limit = document.getElementById('budgetLimit').value;
            
            try {
                const response = await fetch(`${API_BASE_URL}/budgets/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        category: category,
                        limit: parseFloat(limit),
                        period: 'monthly',
                        currency: 'INR'
                    }),
                });
                
                if (response.ok) {
                    budgetForm.reset();
                    loadBudgets();
                }
            } catch (error) {
                alert('Error creating budget');
            }
        });
    }
    
    // Goal form
    const goalForm = document.getElementById('goalForm');
    if (goalForm) {
        goalForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('goalName').value;
            const target = document.getElementById('goalTarget').value;
            const deadline = document.getElementById('goalDeadline').value;
            
            try {
                const response = await fetch(`${API_BASE_URL}/goals/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        name: name,
                        target_amount: parseFloat(target),
                        deadline: deadline,
                        currency: 'INR'
                    }),
                });
                
                if (response.ok) {
                    goalForm.reset();
                    loadGoals();
                }
            } catch (error) {
                alert('Error creating goal');
            }
        });
    }
    
    // Settings form
    const settingsForm = document.getElementById('settingsForm');
    if (settingsForm) {
        settingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currency = document.getElementById('settingsCurrency').value;
            const theme = document.getElementById('settingsTheme').value;
            
            try {
                await fetch(`${API_BASE_URL}/settings/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        currency: currency,
                        theme: theme
                    }),
                });
                alert('Settings saved!');
            } catch (error) {
                alert('Error saving settings');
            }
        });
    }
    
    loadDashboard();
});

// ===== ANALYTICS =====
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/`);
        const data = await response.json();
        
        // Category breakdown chart
        if (charts.category) charts.category.destroy();
        const ctx1 = document.getElementById('categoryChart');
        if (ctx1) {
            charts.category = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: data.category_breakdown.map(c => c.category),
                    datasets: [{
                        data: data.category_breakdown.map(c => c.total),
                        backgroundColor: ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } }
                }
            });
        }
        
        // Trend chart
        if (charts.trend) charts.trend.destroy();
        const ctx2 = document.getElementById('trendChart');
        if (ctx2) {
            charts.trend = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: data.daily_trend.map(d => d.date),
                    datasets: [{
                        label: 'Daily Spending',
                        data: data.daily_trend.map(d => d.total),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } },
                    scales: {
                        y: { ticks: { color: '#cbd5e1' } },
                        x: { ticks: { color: '#cbd5e1' } }
                    }
                }
            });
        }
        
        // Weekly chart
        if (charts.weekly) charts.weekly.destroy();
        const ctx3 = document.getElementById('weeklyChart');
        if (ctx3) {
            const weeks = Object.keys(data.weekly_breakdown).sort((a, b) => a - b);
            charts.weekly = new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: weeks.map(w => `Week ${w}`),
                    datasets: [{
                        label: 'Weekly Spending',
                        data: weeks.map(w => data.weekly_breakdown[w]),
                        backgroundColor: '#06b6d4'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#cbd5e1' } } },
                    scales: {
                        y: { ticks: { color: '#cbd5e1' } },
                        x: { ticks: { color: '#cbd5e1' } }
                    }
                }
            });
        }
        
        // Category stats
        let statsHTML = '';
        data.category_breakdown.forEach(cat => {
            statsHTML += `
                <div class="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
                    <p class="font-semibold">${cat.category}</p>
                    <p class="text-2xl font-bold text-blue-400">₹${cat.total.toFixed(2)}</p>
                    <p class="text-slate-400 text-sm">${cat.count} transaction${cat.count !== 1 ? 's' : ''}</p>
                </div>
            `;
        });
        document.getElementById('categoryStats').innerHTML = statsHTML;
        
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ===== BUDGETS =====
async function loadBudgets() {
    try {
        const response = await fetch(`${API_BASE_URL}/budget-status/`);
        const budgets = await response.json();
        
        let html = '';
        budgets.forEach(budget => {
            const color = budget.is_exceeded ? 'red' : budget.percentage > 80 ? 'yellow' : 'green';
            html += `
                <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-xl p-7 group hover:border-slate-600 hover:shadow-xl transition-all duration-300">
                    <div class="flex justify-between items-start mb-5">
                        <div>
                            <p class="font-bold text-lg text-slate-100">${budget.category}</p>
                            <p class="text-slate-400 text-sm mt-1">Monthly Budget</p>
                        </div>
                        <button onclick="deleteBudget(${budget.id})" class="text-red-400 opacity-0 group-hover:opacity-100 transition text-sm font-medium hover:text-red-300">Delete</button>
                    </div>
                    <div class="space-y-4">
                        <div class="flex justify-between text-sm">
                            <p class="text-slate-400">Spent: <span class="text-slate-200 font-semibold">₹${budget.spent.toFixed(2)}</span></p>
                            <p class="font-bold text-slate-100">${budget.percentage}%</p>
                        </div>
                        <div class="w-full bg-slate-700 rounded-full h-3">
                            <div class="bg-${color}-500 h-3 rounded-full transition-all duration-300" style="width: ${Math.min(budget.percentage, 100)}%"></div>
                        </div>
                        <p class="text-xs text-slate-400">Limit: <span class="font-semibold">₹${budget.limit.toFixed(2)}</span> | Remaining: <span class="font-semibold text-${color}-400">₹${budget.remaining.toFixed(2)}</span></p>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('budgetsList').innerHTML = html || '<p class="text-slate-500">No budgets created yet</p>';
    } catch (error) {
        console.error('Error loading budgets:', error);
    }
}

async function deleteBudget(id) {
    if (confirm('Delete this budget?')) {
        try {
            await fetch(`${API_BASE_URL}/budgets/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            loadBudgets();
        } catch (error) {
            alert('Error deleting budget');
        }
    }
}

// ===== GOALS =====
async function loadGoals() {
    try {
        const response = await fetch(`${API_BASE_URL}/goals/`);
        const goals = await response.json();
        
        let html = '';
        goals.forEach(goal => {
            const progress = (goal.current_amount / goal.target_amount) * 100;
            html += `
                <div class="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-xl p-7 group hover:border-slate-600 hover:shadow-xl transition-all duration-300">
                    <div class="flex justify-between items-start mb-5">
                        <div>
                            <p class="font-bold text-lg text-slate-100">${goal.name}</p>
                            <p class="text-slate-400 text-sm mt-1">Due: ${new Date(goal.deadline).toLocaleDateString()}</p>
                        </div>
                        <button onclick="deleteGoal(${goal.id})" class="text-red-400 opacity-0 group-hover:opacity-100 transition text-sm font-medium hover:text-red-300">Delete</button>
                    </div>
                    <div class="space-y-4">
                        <div class="flex justify-between text-sm">
                            <p class="text-slate-400">Saved: <span class="text-slate-200 font-semibold">₹${goal.current_amount.toFixed(2)}</span></p>
                            <p class="font-bold text-slate-100">${Math.round(progress)}%</p>
                        </div>
                        <div class="w-full bg-slate-700 rounded-full h-3">
                            <div class="bg-emerald-500 h-3 rounded-full transition-all duration-300" style="width: ${Math.min(progress, 100)}%"></div>
                        </div>
                        <p class="text-xs text-slate-400">Target: <span class="font-semibold">₹${goal.target_amount.toFixed(2)}</span></p>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('goalsList').innerHTML = html || '<p class="text-slate-500">No goals created yet</p>';
    } catch (error) {
        console.error('Error loading goals:', error);
    }
}

async function deleteGoal(id) {
    if (confirm('Delete this goal?')) {
        try {
            await fetch(`${API_BASE_URL}/goals/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            loadGoals();
        } catch (error) {
            alert('Error deleting goal');
        }
    }
}

// ===== SETTINGS =====
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/settings/`);
        const settings = await response.json();
        
        if (Array.isArray(settings) && settings.length > 0) {
            document.getElementById('settingsCurrency').value = settings[0].currency || 'INR';
            document.getElementById('settingsTheme').value = settings[0].theme || 'dark';
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Add CSS for nav buttons
const style = document.createElement('style');
style.textContent = `
    .nav-btn {
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s;
        color: #cbd5e1;
        border: 1px solid transparent;
    }
    
    .nav-btn:hover {
        background-color: rgba(51, 65, 85, 0.5);
    }
    
    .nav-btn.active {
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
    }
    
    .hidden {
        display: none;
    }
`;
document.head.appendChild(style);