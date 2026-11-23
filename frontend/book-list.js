app.controller("BookListController", function ($scope, BookService) {

  $scope.books = [];
  $scope.loading = false;
  $scope.errorMessage = "";

  $scope.categories = ["Fiction", "Science", "History"];

  // What the user has typed or selected
  $scope.filters = {
    search: "",
    category: ""
  };

  $scope.loadBooks = function () {
    $scope.loading = true;
    $scope.errorMessage = "";

    BookService.getBooks()
      .then(function (response) {
        $scope.books = response.data;
      })
      .catch(function () {
        $scope.errorMessage = "Could not load books. Please check that the server is running.";
      })
      .finally(function () {
        $scope.loading = false;
      });
  };

  // Show the error message sent by the API, or a general one
  function showError(error) {
    if (error.data && error.data.error) {
      $scope.errorMessage = error.data.error;
    } else {
      $scope.errorMessage = "Something went wrong. Please try again.";
    }
  }

  $scope.borrowBook = function (book) {
    var name = window.prompt("Enter the borrower's name:");

    // The user pressed Cancel
    if (name === null) {
      return;
    }

    if (name.trim() === "") {
      $scope.errorMessage = "Borrower name is required.";
      return;
    }

    BookService.borrowBook(book.id, name.trim())
      .then(function () {
        $scope.loadBooks();
      })
      .catch(showError);
  };

  $scope.returnBook = function (book) {
    BookService.returnBook(book.id, book.borrower_name)
      .then(function () {
        $scope.loadBooks();
      })
      .catch(showError);
  };

  $scope.deleteBook = function (book) {
    var confirmed = window.confirm('Delete "' + book.title + '"?');

    if (!confirmed) {
      return;
    }

    BookService.deleteBook(book.id)
      .then(function () {
        $scope.loadBooks();
      })
      .catch(showError);
  };

  // Load the books as soon as the screen opens
  $scope.loadBooks();
});