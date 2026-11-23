var app = angular.module("libraryApp", ["ngRoute"]);

app.config(function ($routeProvider) {
  $routeProvider
    .when("/books", {
      template: "<h2>Book list will go here</h2>"
    })
    .when("/books/new", {
      template: "<h2>Add book form will go here</h2>"
    })
    .when("/books/:id/edit", {
      template: "<h2>Edit book form will go here</h2>"
    })
    .otherwise({
      redirectTo: "/books"
    })
    .when("/books", {
      templateUrl: "book-list.html",
      controller: "BookListController"
    })
    .when("/books/new", {
      templateUrl: "book-form.html",
      controller: "BookFormController"
    })
    .when("/books/:id/edit", {
      templateUrl: "book-form.html",
      controller: "BookFormController"
    })
    ;
});