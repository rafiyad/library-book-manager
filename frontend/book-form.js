app.controller("BookFormController", function ($scope, $routeParams, $location, BookService) {

  $scope.categories = ["Fiction", "Science", "History"];
  $scope.currentYear = new Date().getFullYear();
  $scope.loading = false;
  $scope.saving = false;
  $scope.errorMessage = "";

  // If the address contains an id (/books/5/edit), we are editing.
  // If not (/books/new), we are adding.
  $scope.bookId = $routeParams.id;
  $scope.isEdit = false;
  if ($scope.bookId !== undefined) {
    $scope.isEdit = true;
  }

  // The values shown in the form
  $scope.book = {
    title: "",
    author: "",
    category: "",
    published_year: null
  };

  function showError(error) {
    if (error.data && error.data.error) {
      $scope.errorMessage = error.data.error;
    } else {
      $scope.errorMessage = "Something went wrong. Please try again.";
    }
  }

  // When editing, load the book and put its values into the form
  if ($scope.isEdit) {
    $scope.loading = true;

    BookService.getBook($scope.bookId)
      .then(function (response) {
        $scope.book.title = response.data.title;
        $scope.book.author = response.data.author;
        $scope.book.category = response.data.category || "";
        $scope.book.published_year = response.data.published_year;
      })
      .catch(showError)
      .finally(function () {
        $scope.loading = false;
      });
  }

  $scope.save = function (form) {
    // Do not call the API if the form has validation errors
    if (form.$invalid) {
      return;
    }

    $scope.saving = true;
    $scope.errorMessage = "";

    var data = {
      title: $scope.book.title,
      author: $scope.book.author,
      category: $scope.book.category || null,
      published_year: $scope.book.published_year
    };

    var request;
    if ($scope.isEdit) {
      request = BookService.updateBook($scope.bookId, data);
    } else {
      request = BookService.addBook(data);
    }

    request
      .then(function () {
        // Saved: go back to the list
        $location.path("/books");
      })
      .catch(showError)
      .finally(function () {
        $scope.saving = false;
      });
  };
});