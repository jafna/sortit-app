'use strict';

/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('IndexController', function($scope) {
  console.log('helo from indexctrl');
})
.controller('SearchBarController', ['$rootScope', '$scope', 'Search', 'AddItem', function($rootScope, $scope, Search, AddItem){
  $scope.autocompleteOptions = {
    options:{
    source: function (request, response) {
      Search.get({searchString:$scope.searchInput, parentItemId:'0'}, function(data){
	var result = [];
        angular.forEach(data.results, function(value, key){
          var split = value.split("::");
          var labeled = {value:split[0], label:split[1]};
          result.push(labeled);
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
      AddItem.save({parentItemId:'0', room_id:'root', item:ui.item.value},function(data){
          if(data.result!=="error"){
            $rootScope.userItems = data.items;
          }
      });
      $scope.searchInput = "";
      return false;
    }
    },
    methods:{}
  }
}]);

