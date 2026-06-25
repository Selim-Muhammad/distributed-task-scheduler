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


function formatLastSeen(lastSeen) {
    const lastSeenSeconds = Number(lastSeen);
    const nowSeconds = Date.now() / 1000;
    const secondsAgo = Math.floor(nowSeconds - lastSeenSeconds);

    if (secondsAgo < 5) {
        return "Just now";
    }

    if (secondsAgo < 60) {
        return `${secondsAgo} seconds ago`;
    }

    const minutesAgo = Math.floor(secondsAgo / 60);
    return `${minutesAgo} minutes ago`;
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

    if (data.workers.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    No active workers detected
                </td>
            </tr>
        `;
        return;
    }

    data.workers.forEach((worker, index) => {
        table.innerHTML += `
            <tr>
                <td>
                    <strong>Worker ${index + 1}</strong>
                    <br>
                    <span class="task-id">${shortId(worker.worker_id)}</span>
                </td>
                <td>${worker.hostname}</td>
                <td>${createStatusBadge(worker.status)}</td>
                <td>${formatLastSeen(worker.last_seen)}</td>
            </tr>
        `;
    });
}


async function loadTasks() {
    const response = await fetch(`${API_BASE_URL}/tasks`);
    const data = await response.json();

    const recentTasksTable = document.getElementById("recentTasksTable");
    const tasksTable = document.getElementById("tasksTable");

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
    const submitButton = document.querySelector(".primary-button");
    const message = document.getElementById("submitMessage");

    const taskType = document.getElementById("taskTypeInput").value.trim();
    const priority = Number(document.getElementById("priorityInput").value);
    const maxRetries = Number(document.getElementById("maxRetriesInput").value);

    if (taskType === "") {
        message.innerText = "Task type cannot be empty.";
        message.className = "error-message";
        return;
    }

    if (priority < 1 || priority > 10) {
        message.innerText = "Priority must be between 1 and 10.";
        message.className = "error-message";
        return;
    }

    if (maxRetries < 0 || maxRetries > 10) {
        message.innerText = "Max retries must be between 0 and 10.";
        message.className = "error-message";
        return;
    }

    submitButton.disabled = true;
    submitButton.innerText = "Submitting...";
    message.innerText = "";

    try {
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

        message.innerText = `Task submitted successfully: ${shortId(data.id)}`;
        message.className = "success-message";

        document.getElementById("taskTypeInput").value = "image_resize";
        document.getElementById("priorityInput").value = 10;
        document.getElementById("maxRetriesInput").value = 2;

        await refreshDashboard();

    } catch (error) {
        message.innerText = "Failed to submit task.";
        message.className = "error-message";
    }

    submitButton.disabled = false;
    submitButton.innerText = "Submit Task";
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