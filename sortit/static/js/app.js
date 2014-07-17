'use strict';

angular.module('SortIt', ['ngRoute', 'SortIt.directives', 'SortIt.services', 'SortIt.controllers', 'ui.autocomplete', 'ui.sortable'])
.config(['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider) {
          $routeProvider
          .when('/:tags', {
            templateUrl: 'static/partials/list-view.html',
            controller: 'ViewController'
          })
          .when('/', {
            templateUrl:'static/partials/index-view.html',
            controller:'IndexController'
          })
          .otherwise({
            redirectTo: '/'
          });

          $locationProvider.html5Mode(true);
        }]);
