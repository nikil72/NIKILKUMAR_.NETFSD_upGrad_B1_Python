function calculateGrade(percent) {
    if (percent >= 80) return "A";
    if (percent >= 50) return "B";
    return "C";
}

function calculatePercentage(score, total) {
    return (score / total) * 100;
}

function isPass(percent) {
    return percent >= 50;
}

module.exports = { calculateGrade, calculatePercentage, isPass };