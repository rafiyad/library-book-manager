# Library Book Manager

A small web app for a librarian. You can add books, edit them, search them, and track who borrowed them.

- **Backend:** Python, Flask, SQLite
- **Frontend:** AngularJS 1.8, Bootstrap 5

## Project structure

```
backend/    Flask API, database, seed script, tests
frontend/   AngularJS app
```

## What you need

- Python 3.10 or newer
- Git
- A web browser

## How to install

```bash
git clone YOUR_REPO_LINK
cd YOUR_REPO_NAME/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, use `venv\Scripts\activate` to activate the environment.

## How to add sample data

This adds 10 sample books. It is safe to run more than once.

```bash
python seed.py
```

## How to run the app

You need two terminals.

**Terminal 1: backend**

```bash
cd backend
source venv/bin/activate
python app.py
```

The API runs at `http://localhost:5000`.

**Terminal 2: frontend**

```bash
cd frontend
python3 -m http.server 8080
```

Open `http://localhost:8080` in your browser.

## How to run the tests

```bash
cd backend
source venv/bin/activate
pytest -v
```

## API endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/api/books` | List books. Optional: `search`, `category` |
| POST | `/api/books` | Add a book |
| GET | `/api/books/<id>` | Get one book |
| PUT | `/api/books/<id>` | Edit a book |
| DELETE | `/api/books/<id>` | Delete a book |
| POST | `/api/books/<id>/borrow` | Borrow a book. Body: `borrower_name` |
| POST | `/api/books/<id>/return` | Return a book. Body: `borrower_name` |

All errors are returned as JSON, for example `{"error": "Title is required"}`.

## Business rules

- Title and author are required.
- Published year must be between 1900 and the current year.
- A borrowed book cannot be borrowed again.
- A borrowed book cannot be deleted until it is returned.

## One difference from the brief

To return a book, the request must include `borrower_name`, and it must match the person who borrowed the book. If the name is missing, the API returns 400. If the name does not match, the API returns 403.

The brief did not ask for this. I added it so a book cannot be returned under the wrong name.

## What I would improve with more time

- Add a borrowing history, so we can see who borrowed each book and when.
- Add login for librarians.
- Add pagination and sorting to the book list.
- Add more tests, including frontend tests.
- Add Docker Compose, so the app starts with one command.
- Replace the browser prompt for the borrower name with a proper pop-up form.

## AI tools

I used an AI assistant (Claude) for this task. I used it for:

- Planning the steps of the project
- Writing the first version of the backend routes, the seed script, and the tests
- Writing the first version of the AngularJS service, controllers, and screens
- Explaining errors and helping me fix them
- Drafting this README

I ran and tested every part myself, and I can explain and change the code.
