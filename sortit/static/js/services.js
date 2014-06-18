'use strict';

angular.module('SortIt.services', ['ngResource'])
.factory('LeftItems', function($resource) {
  return $resource('/_get_left_lane_items');
})
.factory('RightItems', function($resource){
  return $resource('/_get_right_lane_items');
})
.factory('Search', function($resource){
  return $resource('/_search_items', {}, {
    get:{
      method:'GET',
      isArray:false
    }
  });
})
.factory('AddItem', function($resource){
  return $resource('/_add_item', {}, {
    save:{
      method: 'POST',
      isArray: false
    }
  });
});
