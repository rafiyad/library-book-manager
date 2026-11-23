from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db_connection, init_db
from datetime import date
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
CORS(app)  # Allow the frontend (on a different port) to call this API
init_db()  # Initialize the database when the app starts



# Runs for any unexpected crash in the code
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    return jsonify({"error": "Something went wrong on the server"}), 500

@app.errorhandler(HTTPException)
def handle_http_error(error):
    messages = {
        404: "Not found",
        405: "Method not allowed",
    }
    message = messages.get(error.code, error.description)
    return jsonify({"error": message}), error.code


# Convert a database row into a plain dict so it can be returned as JSON
def book_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "category": row["category"],
        "published_year": row["published_year"],
        "is_borrowed": bool(row["is_borrowed"]),  # SQLite stores booleans as 0/1
        "borrower_name": row["borrower_name"],
        "created_at": row["created_at"],
    }

# Check the request body for a book.
# Returns (clean_book, None) if valid, or (None, error_message) if not.
def validate_book(data):
    if not isinstance(data, dict):
        return None, "Request body must be JSON"

    title = data.get("title")
    author = data.get("author")
    category = data.get("category")
    year = data.get("published_year")

    # Title and author are required and can't be blank
    if not isinstance(title, str) or not title.strip():
        return None, "Title is required"

    if not isinstance(author, str) or not author.strip():
        return None, "Author is required"

    # Category is optional, but must be text if given
    if category is not None and not isinstance(category, str):
        return None, "Category must be text"

    # Year is optional, but must be a whole number from 1900 to this year
    current_year = date.today().year
    if year is not None:
        if type(year) is not int or not 1900 <= year <= current_year:
            return None, f"Published year must be between 1900 and {current_year}"

    # Return the cleaned-up values (extra spaces trimmed)
    book = {
        "title": title.strip(),
        "author": author.strip(),
        "category": category.strip() if category else None,
        "published_year": year,
    }
    return book, None


# GET /api/health - simple check that the server is running
@app.get("/api/health")
def health_check():
    return jsonify({"status": "healthy"}), 200

# GET /api/books - list books, optionally filtered by ?search= and ?category=
@app.get("/api/books")
def list_books():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    # "WHERE 1=1" is always true; it lets us append "AND ..." filters below
    sql = "SELECT * FROM books WHERE 1=1"
    params = []

    # Match the search text anywhere in the title or author
    if search:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]

    # Only books in this exact category
    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY id"

    conn = get_db_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify([book_to_dict(row) for row in rows])


# POST /api/books - add a new book
@app.post("/api/books")
def add_book():
    book, error = validate_book(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400  # 400 = bad request (invalid input)

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO books (title, author, category, published_year) VALUES (?, ?, ?, ?)",
        (book["title"], book["author"], book["category"], book["published_year"]),
    )
    conn.commit()  # Save the change to the database
    # Read the new book back (lastrowid is the id SQLite just assigned)
    row = conn.execute("SELECT * FROM books WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()

    return jsonify(book_to_dict(row)), 201  # 201 = created


# Look up one book by id. Returns the row, or None if it doesn't exist.
def find_book (conn, book_id):
    return conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

# GET /api/books/<id> - get a single book
@app.get("/api/books/<int:book_id>")
def get_book(book_id):
    conn = get_db_connection()
    row = find_book(conn, book_id)
    conn.close()

    if row is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book_to_dict(row)), 200



# PUT /api/books/<id> - replace a book's details
@app.put("/api/books/<int:book_id>")
def update_book(book_id):
    conn = get_db_connection()

    # Make sure the book exists first
    if find_book(conn, book_id) is None:
        conn.close()
        return jsonify({"error": "Book not found"}), 404
    # Then make sure the new data is valid
    book, error = validate_book(request.get_json(silent=True))
    if error:
        conn.close()
        return jsonify({"error": error}), 400
    conn.execute(
        "UPDATE books SET title = ?, author = ?, category = ?, published_year = ? WHERE id = ?",
        (book["title"], book["author"], book["category"], book["published_year"], book_id),
    )
    conn.commit()
    # Read it back so the response shows the saved values
    updated_row = find_book(conn, book_id)
    conn.close()

    return jsonify(book_to_dict(updated_row)), 200


# DELETE /api/books/<id> - remove a book
@app.delete("/api/books/<int:book_id>")
def delete_book(book_id):
    conn = get_db_connection()
    if find_book(conn, book_id) is None:
        conn.close()
        return jsonify({"error": "Book not found"}), 404
    if find_book(conn, book_id)["is_borrowed"]:
        conn.close()
        return jsonify({"error": "Cannot delete a borrowed book"}), 409

    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    return "", 204



# borrowing and returning books
# POST /api/books/<id>/borrow - mark a book as borrowed by someone
@app.post("/api/books/<int:book_id>/borrow")
def borrow_book(book_id):
    conn = get_db_connection()
    book = find_book(conn, book_id)

    if book is None:
        conn.close()
        return jsonify({"error": "Book not found"}), 404

    # Can't borrow a book that someone already has
    if book["is_borrowed"]:
        conn.close()
        return jsonify({"error": "Book is already borrowed"}), 409
        
        # The request body must include who is borrowing it
        data = request.get_json(silent=True)

    borrower_name = None
    if isinstance(data, dict):
        borrower_name = data.get("borrower_name")

    if not isinstance(borrower_name, str) or borrower_name.strip() == "":
        conn.close()
        return jsonify({"error": "Borrower name is required"}), 400

    # Flag the book as borrowed and record the borrower
    conn.execute(
        "UPDATE books SET is_borrowed = 1, borrower_name = ? WHERE id = ?",
        (borrower_name.strip(), book_id),
    )
    conn.commit()
    updated_row = find_book(conn, book_id)
    conn.close()

    return jsonify(book_to_dict(updated_row)), 200



# POST /api/books/<id>/return - mark a book as returned
@app.post("/api/books/<int:book_id>/return")
def return_book(book_id):
    conn = get_db_connection()
    book = find_book(conn, book_id)

    if book is None:
        conn.close()
        return jsonify({"error": "Book not found"}), 404

    # Can't return a book that isn't borrowed
    if not book["is_borrowed"]:
        conn.close()
        return jsonify({"error": "Book is not currently borrowed"}), 409

    # Flag the book as returned and clear the borrower
    conn.execute(
        "UPDATE books SET is_borrowed = 0, borrower_name = NULL WHERE id = ?",
        (book_id,),
    )
    conn.commit()
    updated_row = find_book(conn, book_id)
    conn.close()

    return jsonify(book_to_dict(updated_row)), 200

# Start the development server when this file is run directly (python app.py)
if __name__ == "__main__":
    app.run(debug=True, port=5000)


