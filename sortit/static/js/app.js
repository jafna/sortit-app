'use strict';

angular.module('SortIt', ['ngRoute', 'SortIt.directives', 'SortIt.services', 'SortIt.controllers'])
.config(['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider) {
          $routeProvider
          .when('/:tags', {
            templateUrl: 'static/partials/list-view.html',
            controller: 'TagViewController'
          })
          .when('/', {
            templateUrl:'static/partials/index-view.html',
            controller:'IndexViewController'
          })
          .otherwise({
            redirectTo: '/'
          });

          $locationProvider.html5Mode(true);
        }]);
