// Configuration
const API_BASE_URL = 'http://192.168.1.242:8000/api';

// State
let currentSection = 'analytics';
let currentPlatform = 'all';
let currentTaskFilter = 'all';
let currentUserId = '';
let users = [];
let tasks = [];
let analytics = {};

// DOM Elements
const sections = {
    analytics: document.getElementById('analytics-section'),
    tasks: document.getElementById('tasks-section')
};

const navItems = document.querySelectorAll('.nav-item');
const platformTabs = document.querySelectorAll('.tab-btn');
const filterTabs = document.querySelectorAll('.filter-btn');
const analyticsGrid = document.getElementById('analyticsGrid');
const tasksList = document.getElementById('tasksList');
const taskModal = document.getElementById('taskModal');
const taskForm = document.getElementById('taskForm');
const userFilter = document.getElementById('userFilter');
const taskAssignee = document.getElementById('taskAssignee');

// Initialize with error handling
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('App initializing...');
        setupEventListeners();
        console.log('Event listeners setup complete');
        loadInitialData();
        console.log('Data loading started');
        // Register service worker after a delay to avoid blocking
        setTimeout(() => {
            registerServiceWorker();
        }, 1000);
    } catch (error) {
        console.error('Error initializing app:', error);
        document.body.innerHTML = `
            <div style="padding: 2rem; text-align: center;">
                <h2>Error Loading App</h2>
                <p>${error.message}</p>
                <p>Check the browser console for more details.</p>
            </div>
        `;
    }
});

// Register Service Worker for PWA
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        // Unregister any existing service workers first
        navigator.serviceWorker.getRegistrations().then((registrations) => {
            for (let registration of registrations) {
                registration.unregister();
            }
        });
        
        // Register new service worker with correct path
        navigator.serviceWorker.register('./sw.js')
            .then((registration) => {
                console.log('Service Worker registered:', registration);
            })
            .catch((error) => {
                console.log('Service Worker registration failed:', error);
                // Continue without service worker if it fails
            });
    }
}

function setupEventListeners() {
    // Navigation
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const section = item.dataset.section;
            switchSection(section);
        });
    });

    // Platform tabs
    platformTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            platformTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentPlatform = tab.dataset.platform;
            renderAnalytics();
        });
    });

    // Filter tabs
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTaskFilter = tab.dataset.status;
            renderTasks();
        });
    });

    // Task modal
    document.getElementById('addTaskBtn').addEventListener('click', openTaskModal);
    document.getElementById('closeModal').addEventListener('click', closeTaskModal);
    document.getElementById('cancelBtn').addEventListener('click', closeTaskModal);
    taskModal.addEventListener('click', (e) => {
        if (e.target === taskModal) closeTaskModal();
    });

    // Task form
    taskForm.addEventListener('submit', handleTaskSubmit);

    // User filter
    userFilter.addEventListener('change', (e) => {
        currentUserId = e.target.value;
        renderTasks();
    });
}

function switchSection(section) {
    // Update sections
    Object.values(sections).forEach(s => s.classList.remove('active'));
    sections[section].classList.add('active');

    // Update nav items
    navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });

    currentSection = section;

    // Load data if needed
    if (section === 'analytics' && !analytics.tiktok) {
        loadAnalytics();
    } else if (section === 'tasks' && tasks.length === 0) {
        loadTasks();
    }
}

async function loadInitialData() {
    try {
        console.log('Loading initial data...');
        await Promise.all([
            loadUsers(),
            loadAnalytics(),
            loadTasks()
        ]);
        console.log('Initial data loaded successfully');
    } catch (error) {
        console.error('Error loading initial data:', error);
        // Show error message to user
        const errorMsg = document.createElement('div');
        errorMsg.style.cssText = 'padding: 1rem; background: #fee; color: #c00; margin: 1rem; border-radius: 0.5rem;';
        errorMsg.innerHTML = `<strong>Error:</strong> ${error.message}. Make sure the backend server is running on port 8000.`;
        document.querySelector('.container').prepend(errorMsg);
    }
}

async function loadUsers() {
    try {
        console.log('Loading users from:', `${API_BASE_URL}/tasks/users`);
        const response = await fetch(`${API_BASE_URL}/tasks/users`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        users = await response.json();
        console.log('Users loaded:', users);
        
        // Populate user selects
        userFilter.innerHTML = '<option value="">All Users</option>';
        taskAssignee.innerHTML = '<option value="">Unassigned</option>';
        
        users.forEach(user => {
            const option1 = new Option(user.name, user.id);
            const option2 = new Option(user.name, user.id);
            userFilter.appendChild(option1);
            taskAssignee.appendChild(option2);
        });
    } catch (error) {
        console.error('Error loading users:', error);
        // Initialize with empty array if fetch fails
        users = [];
    }
}

async function loadAnalytics() {
    try {
        analyticsGrid.innerHTML = '<div class="loading">Loading analytics...</div>';
        
        console.log('Loading analytics from:', `${API_BASE_URL}/analytics/all`);
        const response = await fetch(`${API_BASE_URL}/analytics/all`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        analytics = await response.json();
        console.log('Analytics loaded:', analytics);
        
        renderAnalytics();
    } catch (error) {
        console.error('Error loading analytics:', error);
        analyticsGrid.innerHTML = `
            <div class="loading" style="color: #c00;">
                Error loading analytics: ${error.message}<br>
                <small>Make sure the backend server is running on port 8000</small>
            </div>
        `;
    }
}

async function loadTasks() {
    try {
        tasksList.innerHTML = '<div class="loading">Loading tasks...</div>';
        
        let url = `${API_BASE_URL}/tasks`;
        const params = new URLSearchParams();
        if (currentTaskFilter !== 'all') {
            params.append('status', currentTaskFilter);
        }
        if (currentUserId) {
            params.append('assigned_to', currentUserId);
        }
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        console.log('Loading tasks from:', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        tasks = await response.json();
        console.log('Tasks loaded:', tasks);
        
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        tasksList.innerHTML = `
            <div class="loading" style="color: #c00;">
                Error loading tasks: ${error.message}<br>
                <small>Make sure the backend server is running on port 8000</small>
            </div>
        `;
    }
}

function renderAnalytics() {
    if (!analytics.tiktok && !analytics.instagram && !analytics.sheets) {
        analyticsGrid.innerHTML = '<div class="loading">No analytics data available.</div>';
        return;
    }

    const platforms = [];
    if (currentPlatform === 'all' || currentPlatform === 'tiktok') {
        if (analytics.tiktok) platforms.push({ ...analytics.tiktok, key: 'tiktok' });
    }
    if (currentPlatform === 'all' || currentPlatform === 'instagram') {
        if (analytics.instagram) platforms.push({ ...analytics.instagram, key: 'instagram' });
    }
    if (currentPlatform === 'all' || currentPlatform === 'sheets') {
        if (analytics.sheets) platforms.push({ ...analytics.sheets, key: 'sheets' });
    }

    if (platforms.length === 0) {
        analyticsGrid.innerHTML = '<div class="loading">No data for selected platform.</div>';
        return;
    }

    analyticsGrid.innerHTML = platforms.map(platform => createAnalyticsCard(platform)).join('');
}

function createAnalyticsCard(platform) {
    const metrics = platform.metrics || {};
    const badgeClass = `badge-${platform.key}`;
    const platformName = platform.key.charAt(0).toUpperCase() + platform.key.slice(1).replace('_', ' ');

    let metricsHtml = '';
    if (platform.key === 'sheets') {
        metricsHtml = `
            <div class="metric-item">
                <div class="metric-value">${metrics.total_orders || 0}</div>
                <div class="metric-label">Total Orders</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">$${formatNumber(metrics.total_revenue || 0)}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${metrics.total_customers || 0}</div>
                <div class="metric-label">Customers</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">$${formatNumber(metrics.average_order_value || 0)}</div>
                <div class="metric-label">Avg Order Value</div>
            </div>
        `;
    } else if (platform.key === 'tiktok') {
        metricsHtml = `
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.followers || 0)}</div>
                <div class="metric-label">Followers</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.views || 0)}</div>
                <div class="metric-label">Views</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.likes || 0)}</div>
                <div class="metric-label">Likes</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics.engagement_rate || 0).toFixed(1)}%</div>
                <div class="metric-label">Engagement Rate</div>
            </div>
        `;
    } else if (platform.key === 'instagram') {
        metricsHtml = `
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.followers || 0)}</div>
                <div class="metric-label">Followers</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.posts || 0)}</div>
                <div class="metric-label">Posts</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${(metrics.engagement_rate || 0).toFixed(1)}%</div>
                <div class="metric-label">Engagement Rate</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">${formatNumber(metrics.reach || 0)}</div>
                <div class="metric-label">Reach</div>
            </div>
        `;
    }

    return `
        <div class="analytics-card">
            <div class="card-header">
                <h3>${platformName}</h3>
                <span class="platform-badge ${badgeClass}">${platformName}</span>
            </div>
            <div class="metric-grid">
                ${metricsHtml}
            </div>
            ${platform.note ? `<div style="margin-top: 1rem; font-size: 0.85rem; color: var(--text-secondary);">${platform.note}</div>` : ''}
        </div>
    `;
}

function renderTasks() {
    let filteredTasks = tasks;

    // Filter by status
    if (currentTaskFilter !== 'all') {
        filteredTasks = filteredTasks.filter(task => task.status === currentTaskFilter);
    }

    // Filter by user
    if (currentUserId) {
        filteredTasks = filteredTasks.filter(task => task.assigned_to == currentUserId);
    }

    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<div class="loading">No tasks found.</div>';
        return;
    }

    tasksList.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');

    // Add event listeners to task actions
    document.querySelectorAll('.task-card').forEach(card => {
        const editBtn = card.querySelector('.edit-task');
        const deleteBtn = card.querySelector('.delete-task');
        const completeBtn = card.querySelector('.complete-task');
        
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                const taskId = editBtn.dataset.taskId;
                openTaskModal(taskId);
            });
        }
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', async () => {
                const taskId = deleteBtn.dataset.taskId;
                if (confirm('Are you sure you want to delete this task?')) {
                    await deleteTask(taskId);
                }
            });
        }
        
        if (completeBtn) {
            completeBtn.addEventListener('click', async () => {
                const taskId = completeBtn.dataset.taskId;
                await updateTaskStatus(taskId, 'completed');
            });
        }
    });
}

function createTaskCard(task) {
    const assignedUser = users.find(u => u.id === task.assigned_to);
    const deadline = task.deadline ? new Date(task.deadline) : null;
    const isOverdue = deadline && deadline < new Date() && task.status !== 'completed';
    
    const statusClass = `status-${task.status}`;
    const cardClass = `task-card ${task.status} ${isOverdue ? 'overdue' : ''}`;
    
    let deadlineHtml = '';
    if (deadline) {
        const formattedDeadline = deadline.toLocaleDateString() + ' ' + deadline.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        deadlineHtml = `<div><strong>Deadline:</strong> ${formattedDeadline}</div>`;
    }

    return `
        <div class="${cardClass}">
            <div class="task-header">
                <div>
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <span class="task-status ${statusClass}">${task.status.replace('_', ' ')}</span>
                </div>
            </div>
            ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
            <div class="task-meta">
                ${assignedUser ? `<div><strong>Assigned to:</strong> ${escapeHtml(assignedUser.name)}</div>` : '<div>Unassigned</div>'}
                ${deadlineHtml}
            </div>
            <div class="task-actions">
                <button class="btn btn-primary btn-sm edit-task" data-task-id="${task.id}">Edit</button>
                ${task.status !== 'completed' ? `<button class="btn btn-sm complete-task" data-task-id="${task.id}" style="background: var(--success-color); color: white;">Complete</button>` : ''}
                <button class="btn btn-danger btn-sm delete-task" data-task-id="${task.id}">Delete</button>
            </div>
        </div>
    `;
}

function openTaskModal(taskId = null) {
    document.getElementById('modalTitle').textContent = taskId ? 'Edit Task' : 'Add Task';
    document.getElementById('taskId').value = taskId || '';
    
    if (taskId) {
        const task = tasks.find(t => t.id == taskId);
        if (task) {
            document.getElementById('taskTitle').value = task.title;
            document.getElementById('taskDescription').value = task.description || '';
            document.getElementById('taskAssignee').value = task.assigned_to || '';
            document.getElementById('taskStatus').value = task.status;
            if (task.deadline) {
                const deadline = new Date(task.deadline);
                document.getElementById('taskDeadline').value = deadline.toISOString().slice(0, 16);
            } else {
                document.getElementById('taskDeadline').value = '';
            }
        }
    } else {
        taskForm.reset();
        document.getElementById('taskId').value = '';
    }
    
    taskModal.classList.add('active');
}

function closeTaskModal() {
    taskModal.classList.remove('active');
    taskForm.reset();
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const taskId = document.getElementById('taskId').value;
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        assigned_to: document.getElementById('taskAssignee').value || null,
        status: document.getElementById('taskStatus').value,
        deadline: document.getElementById('taskDeadline').value || null
    };

    try {
        let response;
        if (taskId) {
            // Update existing task
            response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        } else {
            // Create new task
            response = await fetch(`${API_BASE_URL}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            });
        }

        if (response.ok) {
            closeTaskModal();
            await loadTasks();
        } else {
            const error = await response.json();
            alert('Error saving task: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving task:', error);
        alert('Error saving task. Please try again.');
    }
}

async function deleteTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadTasks();
        } else {
            alert('Error deleting task.');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        alert('Error deleting task. Please try again.');
    }
}

async function updateTaskStatus(taskId, status) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            await loadTasks();
        } else {
            alert('Error updating task.');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        alert('Error updating task. Please try again.');
    }
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

