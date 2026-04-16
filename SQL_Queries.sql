-- ══════════════════════════════════════════════════════
--  ELearn Platform – SQL Reference Queries (SQLite)
-- ══════════════════════════════════════════════════════

-- ── 1. BASIC SELECT / WHERE / ORDER BY ──────────────
SELECT * FROM Courses
WHERE Category = 'Backend'
ORDER BY CreatedAt DESC;

SELECT * FROM Users
WHERE CreatedAt >= date('now', '-30 days')
ORDER BY FullName;

-- ── 2. INNER JOIN ────────────────────────────────────
SELECT c.Title AS Course, u.FullName AS Instructor
FROM Courses c
INNER JOIN Users u ON c.CreatedBy = u.UserId
ORDER BY c.CreatedAt DESC;

SELECT r.ResultId, u.FullName, qz.Title AS Quiz,
       r.Score, r.TotalQuestions, r.AttemptDate
FROM Results r
INNER JOIN Users u ON r.UserId = u.UserId
INNER JOIN Quizzes qz ON r.QuizId = qz.QuizId;

-- ── 3. LEFT JOIN ─────────────────────────────────────
SELECT c.Title,
       COUNT(l.LessonId) AS LessonCount
FROM Courses c
LEFT JOIN Lessons l ON c.CourseId = l.CourseId
GROUP BY c.CourseId, c.Title
ORDER BY LessonCount DESC;

SELECT c.Title,
       COUNT(q.QuizId) AS QuizCount
FROM Courses c
LEFT JOIN Quizzes q ON c.CourseId = q.CourseId
GROUP BY c.CourseId, c.Title;

-- ── 4. AGGREGATION (GROUP BY, COUNT, AVG) ───────────
SELECT qz.Title,
       COUNT(r.ResultId) AS Attempts,
       AVG(CAST(r.Score AS REAL) / r.TotalQuestions * 100) AS AvgPercentage,
       MAX(CAST(r.Score AS REAL) / r.TotalQuestions * 100) AS BestScore
FROM Quizzes qz
LEFT JOIN Results r ON qz.QuizId = r.QuizId
GROUP BY qz.QuizId, qz.Title
ORDER BY Attempts DESC;

-- ── 5. SUBQUERY – Users scoring above average ────────
SELECT DISTINCT u.FullName, u.Email,
       ROUND(CAST(r.Score AS REAL) / r.TotalQuestions * 100, 1) AS ScorePct
FROM Users u
JOIN Results r ON u.UserId = r.UserId
WHERE (CAST(r.Score AS REAL) / r.TotalQuestions * 100) >
    (SELECT AVG(CAST(Score AS REAL) / TotalQuestions * 100) FROM Results)
ORDER BY ScorePct DESC;

-- ── 6. SET OPERATORS (UNION) ─────────────────────────
-- Combined learning activity feed
SELECT 'Enrolled' AS Activity, u.FullName, c.Title AS Target, c.CreatedAt AS EventDate
FROM Courses c JOIN Users u ON c.CreatedBy = u.UserId
UNION
SELECT 'Attempted Quiz', u.FullName, qz.Title, r.AttemptDate
FROM Results r
JOIN Users u ON r.UserId = u.UserId
JOIN Quizzes qz ON r.QuizId = qz.QuizId
ORDER BY EventDate DESC;

-- ── 7. DML – INSERT ──────────────────────────────────
INSERT INTO Courses (Title, Description, Category, CreatedBy, CreatedAt)
VALUES ('New Course', 'Learn something new', 'Backend', 1, datetime('now'));

INSERT INTO Lessons (CourseId, Title, Content, OrderIndex)
VALUES (1, 'Getting Started', 'Intro content here...', 1);

-- ── 8. DML – UPDATE ──────────────────────────────────
UPDATE Courses
SET Title = 'Updated Course Title', Description = 'New description'
WHERE CourseId = 1;

UPDATE Users
SET FullName = 'New Name'
WHERE Email = 'admin@elearn.com';

-- ── 9. DML – DELETE ──────────────────────────────────
DELETE FROM Results WHERE ResultId = 99;
DELETE FROM Lessons WHERE CourseId = 99;

-- ── 10. LEADERBOARD VIEW ─────────────────────────────
SELECT
    u.FullName,
    COUNT(r.ResultId) AS TotalAttempts,
    ROUND(AVG(CAST(r.Score AS REAL) / r.TotalQuestions * 100), 1) AS AvgScore,
    ROUND(MAX(CAST(r.Score AS REAL) / r.TotalQuestions * 100), 1) AS BestScore
FROM Users u
LEFT JOIN Results r ON u.UserId = r.UserId
GROUP BY u.UserId, u.FullName
ORDER BY AvgScore DESC;
