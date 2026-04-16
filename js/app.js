// Table
const table = document.getElementById("courseTable");

if (table) {
    table.innerHTML = "<tr><th>Course</th><th>Status</th></tr>";

    courses.forEach(c => {
        table.innerHTML += `
        <tr>
            <td>${c.name}</td>
            <td>${c.completed ? "Completed" : "Pending"}</td>
        </tr>`;
    });
}

// Progress
const progressBar = document.getElementById("progressBar");

if (progressBar) {
    let completed = courses.filter(c => c.completed).length;
    progressBar.value = (completed / courses.length) * 100;
}

// Cards
const cards = document.getElementById("courseCards");

if (cards) {
    courses.forEach(c => {
        let div = document.createElement("div");

        div.innerHTML = `
            <h3>${c.name}</h3>
            <ol>
                ${c.lessons.map(l => `<li>${l}</li>`).join("")}
            </ol>
        `;

        cards.appendChild(div);
    });
}