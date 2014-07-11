'use strict';

function isURL(str) {
  var pattern = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
  if(!pattern.test(str)) {
    return false;
  }
  return true;
}

function getItemTitle(item){
  return item.slice(5);
}

/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('IndexController',['$rootScope','Item', '$routeParams', '$location', function($rootScope, Item, $routeParams, $location) {
  /* All root scope variables used in this application */
  $rootScope.activeTags = $routeParams.tags === undefined ? [] : $routeParams.tags.split('+');

  Item.users({tags:$rootScope.activeTags},function(data){
    if(data.state==="success"){
      $rootScope.userItems = data.items;
    }
  });

  Item.average({tags:$rootScope.activeTags}, function(data){
    if(data.state==="success"){
      $rootScope.averageItems = data.items;
    }
  });

  $rootScope.resolvingItems = [];

  $rootScope.$watchCollection('activeTags', function(newValue, oldValue){
    $location.path('/'+newValue.join('+'));
  });

  /* Add listener for Server Sent Events  */
  var source = new EventSource('/stream?tags='+$rootScope.activeTags.join('&tags='));
  source.onmessage = function (event) {
    /* sent url has been fetched, so get the item with its title  */
    if(event.data.indexOf('item:')===0){
      var title = getItemTitle(event.data);
      Item.add({tags:$rootScope.activeTags, item:title}, function(data){
        if(data.state==="success"){
          $rootScope.userItems = data.items;
          $rootScope.resolvingItems.pop();
        }
      });
    }else if(event.data === 'averages'){
      Item.average({tags:$rootScope.activeTags}, function(data){
        $rootScope.averageItems = data.items;
      });
    }else if(event.data === 'error'){
      $rootScope.resolvingItems.pop();
    }
    if(event.id === "CLOSE"){
      source.close();
    }
  };

}])


.controller('SearchBarController', ['$rootScope', '$scope', 'Search', 'Item', function($rootScope, $scope, Search, Item){
  $scope.autocompleteOptions = {
    options:{
      source: function (request, response) {
        Search.get({searchString:$scope.searchInput, parentItemId:'0'}, function(data){
          var result = [];
          angular.forEach(data.results, function(value, key){
            /* every response string has 'item:' at front*/
            var sliced = getItemTitle(value);
            result.push(sliced);
          });
          response(result);
        });
      },
      minLength: 1,
      focus: function(event, ui){
        event.preventDefault();
        $scope.searchInput = ui.item.label;
      },
      select: function(event, ui){
        event.preventDefault();
        Item.add({tags:$rootScope.activeTags, item:ui.item.value},function(data){
          if(data.state==="success"){
            $rootScope.userItems = data.items;
          }
        });
        $scope.searchInput = "";
        return false;
      }
    },
    methods:{}
  };

  $scope.submit = function(){
    var text = $scope.searchInput;
    if(text){
      if(isURL(text)){
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
    tolerance:'pointer',
    stop: function(e, ui) {
      var items = $('#sortable').sortable('toArray');
      Item.update({tags:$rootScope.activeTags,items:items});
    }
  };
}]);

