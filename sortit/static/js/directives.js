'use strict';

/* Directives */


angular.module('SortIt.directives', ['SortIt.services'])

.directive('sorting',  function(){
  return {
    templateUrl:'static/partials/sorting.html',
    restrict:'E',
    scope:{userData:'='}
  };
})

.directive('listItems', function(){
  return {
    templateUrl:'static/partials/list-items.html',
    restrict:'E',
    scope:{items:'=', pendingItems:'='},
    link:function(scope){
      scope.resolvingItems = [];
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

.directive('staticItem', function(){
  return {
    templateUrl:'static/partials/static-item.html',
    restrict:'E',
    scope:{item:'='}
  };
})

.directive('draggableItem', function(){
  return {
    templateUrl:'static/partials/draggable-item.html',
    restrict:'E',
    scope:{item:'='}
  };
})

.directive('listActiveChannels', ['Item', function(Item){
  return {
    templateUrl:'static/partials/list-active-channels.html',
    restrict:'E',
    scope:{tags:'='},
    link:function(scope){
      scope.showChannel = function(newTags){
        scope.tags = newTags;
      };

      Item.channels({tags:scope.tags}, function(data){
        if(data.state==="success"){
          scope.channels = data.channels;
        }
      });

    }
  };
}])

.directive('searchBar', ['Item', 'Utils', function(Item, Utils){
  return {
    templateUrl:'static/partials/search-bar.html',
    restrict:'E',
    scope:false,
    link:function(scope){
      var responseFunction = function(data){
        if(data.state === "success"){
          scope.userData.userItems = data.items;
        }else if(data.state === "resolving"){
          scope.userData.pendingItems.push({title:'resolving'});
        }
      };
      scope.submit = function(){
        var string = this.searchInput;
        var i, text;
        if(string){
          var queries = string.split(" ");
          for(i = 0; i<queries.length; i++){
            text = queries[i];
            if(Utils.isURL(text)){
              Item.save({tags:scope.userData.activeTags,url:text}, responseFunction);
            }else if(text.indexOf('#')===0){
              if(!_.contains(scope.userData.activeTags, text.slice(1))){
                scope.userData.activeTags.push(text.slice(1));
              } else {
                throw "Tag already chosen!";
              }
            }
          }
        }
        this.searchInput = "";
      };
    }
  };
}])

.directive('trash', function(){
  return {
    templateUrl:'static/partials/trash.html',
    restrict:'E',
    link:function(scope){
      var trashElement = document.getElementById('trash-list');
      new Sortable(trashElement, 
                   {group:'list-group',
                     onEnd:function(event){
                       _.remove(scope.userData.userItems, function(currentObject) {
                             return currentObject.title === event.item.id;
                       });
                       event.item.remove();
                       scope.$apply(function(){
                         scope.userData.dragging = false;
                       });}
                   });
    }
  };
})

.directive('listActiveTags', ['$location', function($location){
  return {
    templateUrl:'static/partials/list-active-tags.html',
    restrict:'E',
    scope:{tags:'='},
    link:function(scope){
      scope.removeTag = function(tag){
        scope.tags = _.without(scope.tags, tag);
      };
      scope.$watchCollection('tags', function(newValue, oldValue){
        if(!_.isEqual(newValue,oldValue)){
          $location.path('/'+newValue.join('+'));
        }
      });
    }
  };
}]);
