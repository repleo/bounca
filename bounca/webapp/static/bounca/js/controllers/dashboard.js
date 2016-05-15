'use strict';

var app;

app = angular.module('angularDjangoRegistrationAuthApp'); //, ['ngResource']

app.factory('Certificate', [
    '$resource', function($resource) {
      return $resource('/api/v1/certificates/:id', { id: '@id' } );
    }
  ]);

app.controller('DashboardCtrl', ['$scope', '$interval', '$http', '$route', 'Certificate', function($scope, $interval, $http, $route, Certificate) {


	
	$scope.parent_id=$route.current.params.id;
	$scope.parent=null;
	if($scope.parent_id){
		console.log($scope.parent_id);
		Certificate.get({id:$scope.parent_id},function(dataElements){
			console.log(dataElements);
			$scope.parent=dataElements;
		})
	}

	
	
    $scope.search = {
            query: ''
    };
    
    $scope.pagination = {
			totalItems : 0,
			page : 1,
			maxSize : 5
    };
    load_certificates();
	
	$interval(function(){
		load_certificates();
	},60000);

	
	$scope.changedSearchField = function(){
		$scope.pagination = {
				totalItems : 0,
				page : 1,
				maxSize : 5
	    };
		load_certificates();
	};
	
	$scope.nextPage = function(){
		$scope.pagination.page = $scope.pagination.next;
		load_certificates();
	};

	$scope.previousPage = function(){
		$scope.pagination.page = $scope.pagination.previous;
		load_certificates();
	};

	$scope.pageChanged = function () {
		console.log("page changed");
		load_certificates();
	};
	
	
	function load_certificates(){
		var query;
		query={'ordering':'-id','page':$scope.pagination.page}
		
		if($scope.search.query){
			query['search']=$scope.search.query;
		} 
		if($scope.parent_id){
			query['parent']=$scope.parent_id;
		} else {
			query['type']='R';
		}
		
		
		Certificate.get(query,function(dataElements){
				$scope.certs = dataElements.results;
				$scope.pagination.totalItems = dataElements.count;
		});
	}; 
	


}
]);

app.controller('AddRootCACtrl', function($scope, $http, $window, djangoUrl, djangoForm) {
	var postRootCAURL = djangoUrl.reverse('api:v1:certificates');
	var success_url = "/";
	
	$scope.submit = function() {
		if ($scope.root_ca_data) {
			$http.post(postRootCAURL, $scope.root_ca_data).success(function(out_data) {
				if (!djangoForm.setErrors($scope.root_ca_form, out_data.errors)) {
					// on successful post, redirect onto success page
					$window.location.href = success_url;
				}
			}).error(function(out_data) {
				djangoForm.setErrors($scope.root_ca_form, out_data);
				console.log(out_data);
			});
		}
		return false;
	};
});

