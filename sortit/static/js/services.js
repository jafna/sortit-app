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
.factory('Item', function($resource){
  return $resource('/_get_user_items', {}, {
    'users':{isArray:false},
    'average':{isArray:false, url:'/_get_average_items'},
    'add':{method:'POST', isArray:false, url:'/_add_item'},
    'save':{method:'POST', isArray:false, url:'/_add_url'},
    'update':{method:'POST', isArray:false, url:'/_update_order'}
  });
});
