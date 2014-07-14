'use strict';
/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('IndexController',['$rootScope', '$routeParams', 'Item', 'EventSource', 'Utils', function($rootScope, $routeParams, Item, EventSource, Utils) {
  $rootScope.activeTags = $routeParams.tags === undefined ? [] : $routeParams.tags.split('+');

  Item.average({tags:$rootScope.activeTags}, function(data){
    if(data.state==="success"){
      $rootScope.averageItems = data.items;
    }
  });

  Item.users({tags:$rootScope.activeTags},function(data){
    if(data.state==="success"){
      $rootScope.userItems = data.items;
    }
  });
  EventSource.openConnection($rootScope.activeTags);
}])
.controller('SearchBarController', ['$rootScope', '$scope', 'Search', 'Item', 'Utils', function($rootScope, $scope, Search, Item, Utils){
  $scope.autocompleteOptions = {
    options:{
      source: function (request, response) {
        Search.get({searchString:$scope.searchInput}, function(data){
          var result = [];
          angular.forEach(data.results, function(value, key){
            /* every response string has 'item:' at front*/
            var sliced = Utils.getItemTitle(value);
            result.push(sliced);
          });
          response(result);
        });
      },
      minLength: 1,
      focus: function(event){
        event.preventDefault();
        /*$scope.searchInput = ui.item.label;*/
      },
      select: function(event, ui){
        event.preventDefault();
        Item.add({tags:$rootScope.activeTags, item:ui.item.value},function(data){
          if(data.state==="success"){
            $rootScope.userItems = data.items;
          }
        });
        return false;
      }
    },
    methods:{}
  };

  $scope.submit = function(){
    var text = $scope.searchInput;
    if(text){
      if(Utils.isURL(text)){
        Item.save({tags:$rootScope.activeTags,url:text}, function(data){
          if(data.state === "success"){
            $rootScope.userItems = data.items;
          }else if(data.state === "resolving"){
            $rootScope.resolvingItems.push({title:'resolving'});
          }
        });
      }else if(text.indexOf('#')===0){
        $rootScope.activeTags.push(text.slice(1));
      }
      $scope.searchInput = "";
    }
  };
}])
.controller('UserSortableController', ['$rootScope', '$scope', 'Item', function($rootScope, $scope, Item){
  $scope.sortableOptions = {
    connectWith: '.connected-list',
    placeholder: 'hilight',
    tolerance: 'pointer',
    forcePlaceholderSize: true,
    start:function(){
      $rootScope.$apply(function(scope){
        scope.userDragging = true;
      });
    },
    stop: function() {
      var items = $('#sortable').sortable('toArray');
      Item.update({tags:$rootScope.activeTags,items:items});
      $rootScope.$apply(function(scope){
        scope.userDragging = false;
      });
    },

  };
}]);

