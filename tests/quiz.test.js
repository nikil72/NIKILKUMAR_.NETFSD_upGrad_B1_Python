const { calculateGrade, calculatePercentage, isPass } = require('../js/utils');

test("Grade Test", () => {
    expect(calculateGrade(90)).toBe("A");
});

test("Percentage Test", () => {
    expect(calculatePercentage(2, 4)).toBe(50);
});

test("Pass Test", () => {
    expect(isPass(60)).toBe(true);
});