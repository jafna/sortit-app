'use strict';

angular.module('SortIt', ['ngRoute', 'SortIt.directives', 'SortIt.services', 'SortIt.controllers', 'ui.autocomplete'])
.config(['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider) {
          $routeProvider
          .when('/', {
            templateUrl: 'static/partials/list-view.html',
            controller: 'IndexController'
          })
          .otherwise({
            redirectTo: '/'
          });

          $locationProvider.html5Mode(true);
        }]);
