from db import get_db_connection, init_db

BOOKS = BOOKS = [
    ("Dune", "Frank Herbert", "Fiction", 1965),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", 1960),
    ("1984", "George Orwell", "Fiction", 1949),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", 1925),
    ("A Brief History of Time", "Stephen Hawking", "Science", 1988),
    ("Cosmos", "Carl Sagan", "Science", 1980),
    ("The Selfish Gene", "Richard Dawkins", "Science", 1976),
    ("Sapiens", "Yuval Noah Harari", "History", 2011),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", 1997),
    ("The Silk Roads", "Peter Frankopan", "History", 2015),
]


def seed():
    init_db()
    conn = get_db_connection()
    added = 0

    for title, author, category, year in BOOKS:
        existing = conn.execute(
            "SELECT id FROM books WHERE title = ? AND author = ?",
            (title, author),
        ).fetchone()

        if existing is None:
            conn.execute(
                "INSERT INTO books (title, author, category, published_year) VALUES (?, ?, ?, ?)",
                (title, author, category, year),
            )
            added += 1

    conn.commit()
    conn.close()
    print(f"Added {added} books, skipped {len(BOOKS) - added} that already existed.")


if __name__ == "__main__":
    seed()