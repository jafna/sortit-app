'use strict';

/* Directives */


angular.module('SortIt.directives', ['SortIt.services'])

.directive('listItems', function($rootScope){
  return {
    templateUrl:'static/partials/list-items.html',
    restrict:'E',
    scope:{items:'=', pendingItems:'='},
    link:function(){
      $rootScope.resolvingItems = [];
    }
  };
})

.directive('listStaticItems', function(){
  return {
    templateUrl:'static/partials/list-static-items.html',
    restrict:'E',
    scope:{items:'='}
  };
})

.directive('listActiveChannels', ['$rootScope', function($rootScope){
  return {
    templateUrl:'static/partials/list-active-channels.html',
    restrict:'E',
    scope:true,
    link:function(scope){
      $rootScope.channels = [];
      scope.showChannel = function(tags){
        $rootScope.activeTags = tags;
      };
    }
  };
}])

.directive('searchBar', function(){
  return {
    templateUrl:'static/partials/search-bar.html',
    restrict:'E',
    scope:true,
    link:function(scope){
      scope.trash = [];
    }
  };
})

.directive('trash', ['$rootScope', function($rootScope){
  return {
    templateUrl:'static/partials/trash.html',
    restrict:'E',
    scope:true,
    link:function(){
      $rootScope.trash = [];
    }
  };
}])

.directive('listActiveTags', ['$rootScope', '$location', 'EventSource', function($rootScope, $location, EventSource){
  return {
    templateUrl:'static/partials/list-active-tags.html',
    restrict:'E',
    scope:true,
    link:function(scope){
      scope.removeTag = function(tag){
        $rootScope.activeTags = _.without($rootScope.activeTags, tag);
      };
      $rootScope.$watchCollection('activeTags', function(newValue, oldValue){
        if(!_.isEqual(newValue,oldValue)){
          $location.path('/'+newValue.join('+'));
        }
      });
    }
  };
}]);
