'use strict';

var app;

app = angular.module('angularDjangoRegistrationAuthApp'); //, ['ngResource']

app.factory('Certificate', [
    '$resource', function($resource) {
      return $resource('/api/v1/certificates/:id', {  }, {
    	  query: {method:'GET', params:{id:''}, isArray:true},
    	  get: {method:'GET', params: {id: '@id'}},
    	  post: {method:'POST', params:{id: '@id'}},
    	  remove: {method:'DELETE', params:{id: '@id'}}
    	} );
    }
  ]);

app.controller('DashboardCtrl', ['$scope', '$interval', '$http', '$route', 'djangoUrl', 'Certificate', function($scope, $interval, $http, $route, djangoUrl, Certificate) {
	var rootCertificateFormURL = djangoUrl.reverse('bounca:add-root-ca-form')
	var intermediaCertificateFormURL = djangoUrl.reverse('bounca:add-intermediate-ca-form')
	var serverCertificateFormURL = djangoUrl.reverse('bounca:add-server-cert-form')
	var clientCertificateFormURL = djangoUrl.reverse('bounca:add-client-cert-form')

	
	$scope.parent_id=$route.current.params.id;
	$scope.parent=null;
	if($scope.parent_id){
		console.log($scope.parent_id);
		Certificate.get({id:$scope.parent_id},function(dataElements){
			$scope.parent=dataElements;
		})
	}

	$scope.getRootCertForm = function(){
		return rootCertificateFormURL;
	}
	
	$scope.getIntermediateCertForm = function(){
		if($scope.parent_id){
			return intermediaCertificateFormURL+"&parent="+$scope.parent_id;
		}else{
			return rootCertificateFormURL;
		}
	}

	$scope.getServerCertForm = function(){
		if($scope.parent_id){
			return serverCertificateFormURL+"&parent="+$scope.parent_id;
		}else{
			return rootCertificateFormURL;
		}
	}
	
	$scope.getClientCertForm = function(){
		if($scope.parent_id){
			return clientCertificateFormURL+"&parent="+$scope.parent_id;
		}else{
			return rootCertificateFormURL;
		}
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
	


	$scope.pageChanged = function () {
		load_certificates();
	};

	
	$scope.delete_cert= function ($event) {
	    var cert_id = $($event.target).attr('data-cert-id');
		Certificate.remove({id:cert_id},function(dataElements){
			console.log(dataElements);
			load_certificates();
		})
		
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

app.controller('AddCertificateCtrl', function($scope, $http, $window, djangoUrl, djangoForm) {
	var postCertificateURL = djangoUrl.reverse('api:v1:certificates');
	var success_url = $window.location.href;
	
	$scope.submit = function() {
		if ($scope.cert_data) {
			$("#process-busy-modal").modal("show");
			$http.post(postCertificateURL, $scope.cert_data).success(function(out_data) {
				$("#process-busy-modal").modal("hide");
				if (!djangoForm.setErrors($scope.cert_form, out_data.errors)) {
				    var buttons = document.getElementsByClassName('close');
				    for(var i = 0; i <= buttons.length; i++)  
				       buttons[i].click();
				}
			}).error(function(out_data) {
				djangoForm.setErrors($scope.cert_form, out_data);
			});
		}
		return false;
	};
});

