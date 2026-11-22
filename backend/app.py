from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db_connection, init_db
from datetime import date


app = Flask(__name__)
CORS(app)
init_db()  # Initialize the database when the app starts


def book_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "category": row["category"],
        "published_year": row["published_year"],
        "is_borrowed": bool(row["is_borrowed"]),
        "borrower_name": row["borrower_name"],
        "created_at": row["created_at"],
    }

def validate_book(data):
    if not isinstance(data, dict):
        return None, "Request body must be JSON"

    title = data.get("title")
    author = data.get("author")
    category = data.get("category")
    year = data.get("published_year")

    if not isinstance(title, str) or not title.strip():
        return None, "Title is required"

    if not isinstance(author, str) or not author.strip():
        return None, "Author is required"

    if category is not None and not isinstance(category, str):
        return None, "Category must be text"

    current_year = date.today().year
    if year is not None:
        if type(year) is not int or not 1900 <= year <= current_year:
            return None, f"Published year must be between 1900 and {current_year}"

    book = {
        "title": title.strip(),
        "author": author.strip(),
        "category": category.strip() if category else None,
        "published_year": year,
    }
    return book, None


@app.get("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.get("/api/books")
def list_books():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    sql = "SELECT * FROM books WHERE 1=1"
    params = []

    if search:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY id"

    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify([book_to_dict(row) for row in rows])


@app.post("/api/books")
def add_book():
    book, error = validate_book(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO books (title, author, category, published_year) VALUES (?, ?, ?, ?)",
        (book["title"], book["author"], book["category"], book["published_year"]),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()

    return jsonify(book_to_dict(row)), 201




if __name__ == "__main__":
    app.run(debug=True, port=5000)


