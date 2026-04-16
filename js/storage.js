const list = document.getElementById("completedCourses");

if (list) {
    let score = localStorage.getItem("score");

    if (score) {
        let li = document.createElement("li");
        li.innerText = "Quiz Score: " + score + "%";
        list.appendChild(li);
    }
}