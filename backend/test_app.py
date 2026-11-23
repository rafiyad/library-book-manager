import pytest

import db
from app import app


# Give each test its own empty database file, so tests never touch database.db
@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app.config["TESTING"] = True
    return app.test_client()


# Adding a valid book returns 201 and the saved book
def test_add_book(client):
    res = client.post("/api/books", json={"title": "Dune", "author": "Frank Herbert"})

    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Dune"
    assert data["is_borrowed"] is False


# Adding a book without a title is rejected with 400
def test_add_book_without_title(client):
    res = client.post("/api/books", json={"author": "Frank Herbert"})

    assert res.status_code == 400
    assert res.get_json()["error"] == "Title is required"


# A book can be borrowed once, but not borrowed again until it is returned
def test_borrow_book(client):
    book_id = client.post("/api/books", json={"title": "Dune", "author": "Frank Herbert"}).get_json()["id"]

    res = client.post(f"/api/books/{book_id}/borrow", json={"borrower_name": "Alice"})
    assert res.status_code == 200
    assert res.get_json()["borrower_name"] == "Alice"

    res = client.post(f"/api/books/{book_id}/borrow", json={"borrower_name": "Bob"})
    assert res.status_code == 409
