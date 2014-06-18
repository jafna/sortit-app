'use strict';

/* Directives */


angular.module('SortIt.directives', ['SortIt.services'])

.directive('listLeftLane', ['LeftItems', function(LeftItems){
  return {
    templateUrl:'static/partials/list-left-lane.html',
    restrict:'E',
    scope:true,
    link:function(scope, element, attrs){
        scope.averages = [];
        LeftItems.get({parentItemId:'0'}, function(data){
            scope.averages = data.items;
        });
    }
  };
}])

.directive('listRightLane',['$rootScope', 'RightItems', function($rootScope, RightItems){
  return {
    templateUrl:'static/partials/list-right-lane.html',
    restrict:'E',
    scope:true,
    link:function(scope, element, attrs){
        scope.items = [];
        RightItems.get({parentItemId:'0'}, function(data){
            $rootScope.userItems = data.items;
        });
    }
  };
}])

.directive('searchBar', function(){
  return {
    templateUrl:'static/partials/search-bar.html',
    restrict:'E',
    scope:true,
    link:function(scope, element, attrs){
        
    }
  };
});
