'use strict';

angular.module('angularDjangoRegistrationAuthApp')
  .controller('MasterCtrl', function ($scope, $location, djangoAuth) {
    // Assume user is not logged in until we hear otherwise
    $scope.authenticated = false;
    // Wait for the status of authentication, set scope var to true if it resolves
    djangoAuth.authenticationStatus(true).then(function(){
        djangoAuth.profile().then(function(data){
    	  	if(data.first_name){
    	  		$scope.name=data.first_name;
    	  	} else {
    	  		$scope.name=data.username;
    	  	}
            $scope.authenticated = true;

          });
    });
    // Wait and respond to the logout event.
    $scope.$on('djangoAuth.logged_out', function() {
      $scope.authenticated = false;
    });
    // Wait and respond to the log in event.
    $scope.$on('djangoAuth.logged_in', function() {
      djangoAuth.profile().then(function(data){
	  	if(data.first_name){
	  		$scope.name=data.first_name;
	  	} else {
	  		$scope.name=data.username;
	  	}
        $scope.authenticated = true;

      });
    });
    // If the user attempts to access a restricted page, redirect them back to the main page.
    $scope.$on('$routeChangeError', function(ev, current, previous, rejection){
      console.error("Unable to change routes.  Error: ", rejection)
      $location.path('/restricted').replace();
    });
    
    $scope.logout = function(){
        djangoAuth.logout()
        .then(handleSuccess,handleError);
    }
    var handleSuccess = function(data){
        $scope.response = data;
      }
      
    var handleError = function(data){
        $scope.response = data;
      }    
  });


