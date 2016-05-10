'use strict';

var app;

app = angular.module('angularDjangoRegistrationAuthApp'); //, ['ngResource']

app.factory('Certificate', [
    '$resource', function($resource) {
      return $resource('/api/v1/certificates', {
      });
    }
  ]);

app.controller('DashboardCtrl', ['$scope', '$interval', '$http', 'Certificate', function($scope, $interval, $http, Certificate) {
    $scope.search = {
            query: ''
    };
    $scope.pagination = {
            page: 1,
            previous: 1,
            next: 1
    };
    load_certificates();
	
	$interval(function(){
		load_certificates();
	},60000);

	
	$scope.changedSearchField = function(){
		$scope.pagination = {
	            page: 1,
	            previous: 1,
	            next: 1
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
	
	
	function load_certificates(){
		var query;
		if($scope.search.query){
			query={'ordering':'-expires_at','type':'R','page':$scope.pagination.page,search:$scope.search.query}
		} else {
			query={'ordering':'-expires_at','type':'R','page':$scope.pagination.page}
		}
		Certificate.get(query,function(dataElements){
				$scope.certs = dataElements.results;
				if(dataElements.previous==null)
					$scope.pagination.previous = 1;
				else
					$scope.pagination.previous = $scope.pagination.page - 1;
				if(dataElements.next==null)
					$scope.pagination.next = $scope.pagination.page;
				else
					$scope.pagination.next = $scope.pagination.page + 1;
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
				//alert('An error occured during submission, see browser logs (TODO add feedback to FORM)');
			});
		}
		return false;
	};
});

