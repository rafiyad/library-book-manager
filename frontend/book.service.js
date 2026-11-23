app.service("BookService", function ($http) {

  var API_URL = "http://localhost:5000/api/books";

  // Get the list of books, with optional search text and category
  this.getBooks = function (search, category) {
    var params = {};

    if (search) {
      params.search = search;
    }

    if (category) {
      params.category = category;
    }

    return $http.get(API_URL, { params: params });
  };

  // Get one book by its id
  this.getBook = function (id) {
    return $http.get(API_URL + "/" + id);
  };

  // Add a new book
  this.addBook = function (book) {
    return $http.post(API_URL, book);
  };

  // Save changes to an existing book
  this.updateBook = function (id, book) {
    return $http.put(API_URL + "/" + id, book);
  };

  // Delete a book
  this.deleteBook = function (id) {
    return $http.delete(API_URL + "/" + id);
  };

  // Mark a book as borrowed
  this.borrowBook = function (id, borrowerName) {
    return $http.post(API_URL + "/" + id + "/borrow", { borrower_name: borrowerName });
  };

  // Mark a book as returned
  this.returnBook = function (id, borrowerName) {
    return $http.post(API_URL + "/" + id + "/return", { borrower_name: borrowerName });
  };
});