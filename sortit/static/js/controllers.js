'use strict';

function isURL(url) {
  var strRegex = "^((https|http|ftp|rtsp|mms)?://)"
  + "?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?"
  + "(([0-9]{1,3}\.){3}[0-9]{1,3}"
  + "|"
  + "([0-9a-z_!~*'()-]+\.)*"
  + "([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]\."
  + "[a-z]{2,6})"
  + "(:[0-9]{1,4})?"
  + "((/?)|"
  + "(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$";
  var re=new RegExp(strRegex);
  return re.test(url);
}

function getItemTitle(item){
  return item.slice(5);
}

/* Controllers */
angular.module('SortIt.controllers', ['SortIt.services'])
.controller('IndexController',['$rootScope','Item', '$routeParams', '$location', function($rootScope, Item, $routeParams, $location) {
  $rootScope.activeTags = $routeParams.tags === undefined ? [] : $routeParams.tags.split('+');

  $rootScope.$watchCollection('activeTags', function(newValue, oldValue){
    Item.users({tags:newValue}, function(data){
      if(data.result!=="error"){
        $rootScope.userItems = data.items;
      }
    });
    Item.average({tags:newValue}, function(data){
      if(data.result!=="error"){
        $rootScope.averageItems = data.items;
      }
    });
    $location.path('/'+newValue.join('+'));
  });

  /* Add listener for Server Sent Events  */
  var source = new EventSource('/stream?tags='+$rootScope.activeTags.join('&tags='));
  source.onmessage = function (event) {
    /* sent url has been fetched, so get the item with its title  */
    if(event.data.indexOf('item:')===0){
      var title = getItemTitle(event.data);
      Item.add({tags:$rootScope.activeTags, item:title}, function(data){
        if(data.result!=="error"){
          $rootScope.userItems = data.items;
        }
      });
    }else if(event.data === 'averages'){
      Item.average({tags:$rootScope.activeTags}, function(data){
        $rootScope.averageItems = data.items;
      });
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
          if(data.result!=="error"){
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
        Item.save({tags:$rootScope.activeTags,url:text});
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

