'use strict';

angular.module('SortIt.services', ['ngResource'])

.factory('AverageItems', function($resource) {
  return $resource('/_get_average_items');
})

.factory('Search', function($resource){
  return $resource('/_search_items', {}, {
    get:{
      method:'GET',
      isArray:false
    }
  });
})

.factory('UserData', function(){
  return { activeTags:[],
            userItems:[],
         averageItems:[],
         pendingItems:[],
             channels:[],
             dragging:false};
})

.factory('Item', function($resource){
  return $resource('/_get_user_items', {}, {
    'users':{isArray:false},
    'average':{isArray:false, url:'/_get_average_items'},
    'channels':{isArray:false, url:'/_get_active_channels'},
    'add':{method:'POST', isArray:false, url:'/_add_item'},
    'save':{method:'POST', isArray:false, url:'/_add_url'},
    'update':{method:'POST', isArray:false, url:'/_update_order'}
  });
})

//Small utils that are used here and there
.service('Utils', function(){
  this.isURL = function(str) {
    var pattern = /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-]*)?\??(?:[\-\+=&;%@\.\w]*)#?(?:[\.\!\/\\\w]*))?)/g;
    if(!pattern.test(str)) {
      return false;
    }
    return true;
  };

  this.getItemTitle = function(item){
    return item.slice(5);
  };

})

//Service that handles SSE connection between server and browser
.service('EventSource', ['Item', 'Utils', function(Item, Utils){
  this.updateConnection = function(scope){
    if(scope.event){
      scope.event.close();
    }
    var activeTags = scope.userData.activeTags;
    /* Add listener for Server Sent Events  */
    scope.event = new EventSource('/stream?tags='+activeTags.join('&tags='));
    scope.event.onmessage = function (event) {
      /* sent url has been fetched, so get the item with its title  */
      if(event.data.indexOf('item:')===0){
        var title = Utils.getItemTitle(event.data);
        Item.add({tags:activeTags, item:title}, function(data){
          if(data.state==="success"){
            scope.userData.userItems = data.items;
            scope.userData.resolvingItems.pop();
          }
        });
      }else if(event.data === 'averages'){
        Item.average({tags:activeTags}, function(data){
          scope.userData.averageItems = data.items;
        });
      }else if(event.data === 'error'){
        scope.userData.resolvingItems.pop();
      }
      if(event.id === "CLOSE"){
        scope.event.close();
      }
    };
  };
}]);
