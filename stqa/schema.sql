-- schema.sql

DROP TABLE IF EXISTS todos;

CREATE TABLE todos (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);

INSERT INTO todos (task, done) VALUES
('Learn Flask fundamentals', 1),
('Build a Todo List App', 1),
('Switch to using SQLite', 1),
('Perform black-box testing', 0),
('Perform white-box testing', 0);