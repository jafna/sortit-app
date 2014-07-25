'use strict';
/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('MainController', ['$scope', 'EventSource', 'UserData', function($scope, EventSource, UserData){
  $scope.userData = UserData;
  $scope.$watchCollection('userData.activeTags', function(){
    EventSource.updateConnection($scope);
  });
}])
.controller('IndexViewController', ['UserData', function(UserData){
  UserData.activeTags = [];
}])
.controller('TagViewController',['$scope', '$routeParams', 'Item', 'UserData', function($scope, $routeParams, Item, UserData) {
  $scope.userData = UserData;
  $scope.userData.activeTags = $routeParams.tags.split('+');

  Item.average({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      $scope.userData.averageItems = data.items;
    }
  });

  Item.users({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      $scope.userData.userItems = data.items;
    }
  });

  Item.channels({tags:$scope.userData.activeTags}, function(data){
    if(data.state==="success"){
      $scope.userData.channels = data.channels;
    }
  });
}])

.controller('SearchBarController', ['$scope', 'UserData', 'Item', 'Search', 'Utils', function($scope, UserData, Item, Search, Utils){
  $scope.userData = UserData;
  var autocompleteParentElement = document.getElementById('autocomplete-container');
  var autocomplete = completely(autocompleteParentElement, {inputId:'search-input', fontSize : '24px', color:'#933', maxResults:6});
  autocomplete.options = [];
  autocomplete.onChange = function(text){
    Search.get({searchString:text}, function(data){
      var result = [];
      angular.forEach(data.results, function(value, key){
        /* every response string has 'item:' at front*/
        var sliced = Utils.getItemTitle(value);
        result.push(sliced);
      });
      autocomplete.options = result;
      autocomplete.repaint();
    });
  };
  autocomplete.onSelection = function(value){
    Item.add({tags:$scope.userData.activeTags, item:value},function(data){
      if(data.state==="success"){
        $scope.userData.userItems = data.items;
      }
    });
  };
  autocomplete.enterWithoutDropDown = function(){
    $scope.submit();
  };
  autocomplete.repaint();
  //<input id="search-input" ng-model="searchInput" class="search-input" type="text" placeholder="Type hashtag, item title or introduce a new item from URL." autocomplete="off" ng-model="searchInput" ui-autocomplete="autocompleteOptions"/>
}])

.controller('UserSortableController', ['$scope', 'Item', 'UserData', function($scope, Item, UserData){
  $scope.userData = UserData;
  var sortableElement = document.getElementById('sortable');
  new Sortable(sortableElement,
               {group:'list-group',
                 store:
                   {get:function(){
                   Item.users({tags:$scope.userData.activeTags}, function(data){
                     if(data.state==="success"){
                       $scope.userData.userItems = data.items;
                     }
                   });
                   return $scope.userData.userItems;
                 },
                 set:function(sortable){
                   Item.update({tags:$scope.userData.activeTags,items:sortable.toArray()});
                 }},
                 onStart:function(){
                   $scope.$apply(function(){
                     $scope.userData.dragging = true;
                   });
                 },
                 onEnd:function(){
                   $scope.$apply(function(){
                     $scope.userData.dragging = false;
                   });}
               });
}]);

