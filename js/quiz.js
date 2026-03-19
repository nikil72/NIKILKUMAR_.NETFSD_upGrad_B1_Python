async function loadQuiz() {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const form = document.getElementById("quizForm");
    form.innerHTML = "";

    quizQuestions.forEach((q, i) => {
        let div = document.createElement("div");

        div.innerHTML = `<p>${q.question}</p>` +
            q.options.map(opt =>
                `<input type="radio" name="q${i}" value="${opt}"> ${opt}<br>`
            ).join("");

        form.appendChild(div);
    });
}

function submitQuiz() {
    let score = 0;

    quizQuestions.forEach((q, i) => {
        let ans = document.querySelector(`input[name="q${i}"]:checked`);
        if (ans && ans.value === q.answer) score++;
    });

    let percent = (score / quizQuestions.length) * 100;

    let grade;
    if (percent >= 80) grade = "A";
    else if (percent >= 50) grade = "B";
    else grade = "C";

    let message;
    switch (grade) {
        case "A": message = "Excellent 🎉"; break;
        case "B": message = "Good 👍"; break;
        default: message = "Improve 💡";
    }

    document.getElementById("result").innerHTML =
        `Score: ${score}<br>Percentage: ${percent}%<br>Grade: ${grade}<br>${message}`;

    localStorage.setItem("score", percent);
}