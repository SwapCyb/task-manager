// Load tasks from backend
async function loadTasks() {
    try {
        const res = await fetch('/tasks');
        const tasks = await res.json();
        const ul = document.getElementById('taskList');
        if (!Array.isArray(tasks)) {
            ul.innerHTML = '<li>Error loading tasks</li>';
            console.error("Unexpected response:", tasks);
            return;
        }
        ul.innerHTML = tasks.map(t => `
      <li>
        <span class="${t.status === 'done' ? 'done' : ''}">
          ${t.title} (${t.status})
        </span>
        <button onclick="toggleStatus(${t.id}, '${t.status}')">
          ${t.status === 'done' ? 'Undo' : 'Done'}
        </button>
        <button onclick="removeTask(${t.id})">Delete</button>
      </li>
    `).join('');
    } catch (err) {
        console.error("Failed to load tasks:", err);
        document.getElementById('taskList').innerHTML = '<li>Could not load tasks</li>';
    }
}
// Add a new task
async function addTask() {
    const title = document.getElementById('newTitle').value.trim();
    if (!title) return alert('Enter a task');
    await fetch('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    document.getElementById('newTitle').value = '';
    loadTasks();
}

// Toggle task status
async function toggleStatus(id, current) {
    const next = current === 'done' ? 'pending' : 'done';
    await fetch(`/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: next })
    });
    loadTasks();
}

// Delete a task
async function removeTask(id) {
    await fetch(`/tasks/${id}`, { method: 'DELETE' });
    loadTasks();
}

// Weather API integration (Open-Meteo, free, no key)
async function loadWeather() {
    const city = document.getElementById('city').value.trim();
    if (!city) return alert('Enter a city');

    // Geocoding to get lat/lon
    const g = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1`);
    const gjson = await g.json();
    if (!gjson.results || !gjson.results.length) {
        document.getElementById('weatherOut').textContent = 'City not found.';
        return;
    }
    const { latitude, longitude } = gjson.results[0];

    // Fetch current weather
    const w = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,wind_speed_10m`);
    const wjson = await w.json();
    document.getElementById('weatherOut').textContent = JSON.stringify(wjson.current, null, 2);
}

// Load tasks on page open
loadTasks();