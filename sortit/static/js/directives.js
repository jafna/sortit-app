'use strict';

/* Directives */


angular.module('SortIt.directives', ['SortIt.services'])

.directive('listItems', function(){
  return {
    templateUrl:'static/partials/list-items.html',
    restrict:'E',
    scope:{items:'=', resolvingItems:'='},
    link:function(scope, element, attrs){
    }
  };
})

.directive('listStaticItems', function(){
  return {
    templateUrl:'static/partials/list-static-items.html',
    restrict:'E',
    scope:{items:'='},
    link:function(scope, element, attrs){
    }
  };
})

.directive('listPendingItems', function(){
  return {
    templateUrl:'static/partials/list-pending-items.html',
    restrict:'E',
    scope:{items:'='},
    link:function(scope, element, attrs){
    }
  };
})

.directive('searchBar', function(){
  return {
    templateUrl:'static/partials/search-bar.html',
    restrict:'E',
    scope:true,
    link:function(scope, element, attrs){
    }
  };
})

.directive('listActiveTags', ['$rootScope', function($rootScope){
  return {
    templateUrl:'static/partials/list-active-tags.html',
    restrict:'E',
    scope:true,
    link:function(scope,element,attrs){
      scope.removeTag = function(tag){
        $rootScope.activeTags = _.without($rootScope.activeTags, tag);
      };
    }
  }
}]);
