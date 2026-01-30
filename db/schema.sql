CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE NOT NULL,
    titre TEXT NOT NULL,
    auteur TEXT,
    edition TEXT,
    scan_date DATE NOT NULL,
    scan_count INTEGER DEFAULT 1
);

-- Index perf
CREATE INDEX idx_date ON books(scan_date);
