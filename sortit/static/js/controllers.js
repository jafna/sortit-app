'use strict';
/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('MainController', ['$scope', 'EventSource', 'UserData', function($scope, EventSource, UserData){
  $scope.userData = UserData;
  $scope.$watchCollection('userData.activeTags', function(){
    EventSource.updateConnection($scope);
  });
}])
.controller('IndexViewController', function(){
  console.log("index");
})
.controller('TagViewController',['$scope', '$routeParams', 'Item', 'UserData', function($scope, $routeParams, Item, UserData) {
  UserData.activeTags = $routeParams.tags.split('+');
  $scope.userData = UserData;

  Item.average({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      UserData.averageItems = data.items;
    }
  });

  Item.users({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      UserData.userItems = data.items;
    }
  });

  Item.channels({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      UserData.channels = data.channels;
    }
  });
}])

.controller('SearchBarController', ['$scope', 'UserData', 'Item', 'Search', 'Utils', function($scope, UserData, Item, Search, Utils){
  $scope.userData = UserData;
  $scope.autocompleteOptions = {
    options:{
      source: function (request, response) {
        Search.get({searchString:$scope.searchInput}, function(data){
          var result = [];
          angular.forEach(data.results, function(value){
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
        /*scope.searchInput = ui.item.label;*/
      },
      select: function(event, ui){
        event.preventDefault();
        Item.add({tags:$scope.userData.activeTags, item:ui.item.value},function(data){
          if(data.state==="success"){
            $scope.userData.userItems = data.items;
          }
        });
        $scope.searchInput = "";
        return false;
      }
    },
    methods:{}
  };
}])

.controller('UserSortableController', ['$scope', 'Item', 'UserData', function($scope, Item, UserData){
  $scope.sortableOptions = {
    connectWith: '.connected-list',
    placeholder: 'hilight',
    tolerance: 'pointer',
    forcePlaceholderSize: true,
    start:function(){
      $scope.$apply(function(){
        UserData.dragging = true;
      });
    },
    stop: function() {
      var items = $('#sortable').sortable('toArray');
      Item.update({tags:$scope.activeTags,items:items});
      $scope.$apply(function(){
        UserData.dragging = false;
      });
    },

  };
}]);

