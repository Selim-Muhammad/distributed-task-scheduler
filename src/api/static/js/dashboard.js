const API_BASE_URL = "http://127.0.0.1:8000";


function showPage(pageId) {
    const pages = document.querySelectorAll(".page");
    const navItems = document.querySelectorAll(".nav-item");

    pages.forEach(page => {
        page.classList.remove("active-page");
    });

    navItems.forEach(item => {
        item.classList.remove("active");
    });

    document.getElementById(pageId).classList.add("active-page");

    event.target.classList.add("active");
}


function createStatusBadge(status) {
    const normalizedStatus = status.toLowerCase();

    return `
        <span class="badge badge-${normalizedStatus}">
            ${status}
        </span>
    `;
}


function shortId(id) {
    return id.substring(0, 8) + "...";
}


async function loadStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    const data = await response.json();

    document.getElementById("queueDepth").innerText = data.queue_depth;
    document.getElementById("aliveWorkers").innerText = data.alive_workers;
    document.getElementById("completedTasks").innerText = data.completed_tasks;
    document.getElementById("pendingTasks").innerText = data.pending_tasks;
    document.getElementById("runningTasks").innerText = data.running_tasks;
    document.getElementById("deadTasks").innerText = data.dead_tasks;
}


async function loadWorkers() {
    const response = await fetch(`${API_BASE_URL}/workers`);
    const data = await response.json();

    const table = document.getElementById("workersTable");
    table.innerHTML = "";

    data.workers.forEach(worker => {
        table.innerHTML += `
            <tr>
                <td class="task-id">${shortId(worker.worker_id)}</td>
                <td>${worker.hostname}</td>
                <td>${createStatusBadge(worker.status)}</td>
                <td>${Number(worker.last_seen).toFixed(0)}</td>
            </tr>
        `;
    });
}


async function loadTasks() {
    const response = await fetch(`${API_BASE_URL}/tasks`);
    const data = await response.json();

    const recentTasksTable =
        document.getElementById("recentTasksTable");

    const tasksTable =
        document.getElementById("tasksTable");

    recentTasksTable.innerHTML = "";
    tasksTable.innerHTML = "";

    data.tasks.forEach(task => {
        const row = `
            <tr>
                <td class="task-id">${shortId(task.id)}</td>
                <td>${task.task_type}</td>
                <td>${task.priority}</td>
                <td>${createStatusBadge(task.status)}</td>
                <td>${task.retry_count}/${task.max_retries}</td>
            </tr>
        `;

        recentTasksTable.innerHTML += row;
        tasksTable.innerHTML += row;
    });
}


async function submitTask() {
    const taskType =
        document.getElementById("taskTypeInput").value;

    const priority =
        Number(document.getElementById("priorityInput").value);

    const maxRetries =
        Number(document.getElementById("maxRetriesInput").value);

    const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            task_type: taskType,
            priority: priority,
            max_retries: maxRetries
        })
    });

    const data = await response.json();

    document.getElementById("submitMessage").innerText =
        `Task submitted: ${shortId(data.id)}`;

    await refreshDashboard();
}


async function refreshDashboard() {
    await loadStats();
    await loadWorkers();
    await loadTasks();
}


refreshDashboard();

setInterval(
    refreshDashboard,
    3000
);