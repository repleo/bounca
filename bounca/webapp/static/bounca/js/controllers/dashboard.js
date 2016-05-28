"use strict";

var app;

app = angular.module("angularDjangoRegistrationAuthApp"); //, ["ngResource"]

app.factory("Certificate", [
    "$resource", function($resource) {
      return $resource("/api/v1/certificates/:id", {  }, {
    	  query: {method:"GET", params:{id:""}, isArray:true},
    	  get: {method:"GET", params: {id: "@id"}},
    	  post: {method:"POST", params:{id: "@id"}},
    	  remove: {method:"DELETE", params:{id: "@id"}}
    	} );
    }
  ]);

app.controller("DashboardCtrl", ["$scope", "$interval", "$http", "$route", "djangoUrl", "Certificate", function($scope, $interval, $http, $route, djangoUrl, Certificate) {
	var rootCertificateFormURL = djangoUrl.reverse("bounca:add-root-ca-form")
	var intermediaCertificateFormURL = djangoUrl.reverse("bounca:add-intermediate-ca-form")
	var serverCertificateFormURL = djangoUrl.reverse("bounca:add-server-cert-form")
	var clientCertificateFormURL = djangoUrl.reverse("bounca:add-client-cert-form")
	var certificateRevokeFormURL = djangoUrl.reverse("bounca:cert-revoke-form")
	var certificateCRLFormURL = djangoUrl.reverse("bounca:cert-crl-file-form")

	
	$scope.parent_id=$route.current.params.id;
	$scope.parent=null;
	if($scope.parent_id){
		Certificate.get({id:$scope.parent_id},function(dataElements){
			$scope.parent=dataElements;
		})
	}
	$scope.getCrlFileForm = function(){
		return certificateCRLFormURL;
	}
	
	
	$scope.getCertRevokeForm = function(){
		return certificateRevokeFormURL;
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
            query: ""
    };
    
    $scope.pagination = {
			totalItems : 0,
			page : 1,
			maxSize : 5
    };
    
    
	function load_certificates(){
		var query;
		query={"ordering":"-id","page":$scope.pagination.page}
		
		if($scope.search.query){
			query.search=$scope.search.query;
		} 
		if($scope.parent_id){
			query.parent=$scope.parent_id;
		} else {
			query.type="R";
		}
		
		
		Certificate.get(query,function(dataElements){
				$scope.certs = dataElements.results;
				$scope.pagination.totalItems = dataElements.count;
		});
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

    $scope.$on("certificate-list-updated", function(){
        load_certificates();
     });	

}
]);

app.controller("AddCertificateCtrl", function($scope, $http, $window, djangoUrl, djangoForm) {
	var postCertificateURL = djangoUrl.reverse("api:v1:certificates");
	var success_url = $window.location.href;
	
	$scope.submit = function() {
		if ($scope.cert_data) {
			var cert_data=$scope.cert_data
			if(cert_data.dn.subjectAltNames){
				if (typeof cert_data.dn.subjectAltNames === "string") {
					var altNames=cert_data.dn.subjectAltNames.split(",");
					cert_data.dn.subjectAltNames=altNames;
				}
			} else {
				cert_data.dn.subjectAltNames=[];
			}
			$("#process-busy-modal").modal("show");
			$http.post(postCertificateURL, cert_data).success(function(out_data) {
				$("#process-busy-modal").modal("hide");
				if (!djangoForm.setErrors($scope.cert_form, out_data.errors)) {
				    var buttons = document.getElementsByClassName("close");
				    $scope.$emit("certificate-list-updated", {});

				    for(var i = 0; i < buttons.length; i++)  
				    	buttons[i].click();
				}
			}).error(function(out_data) {
				$("#process-busy-modal").modal("hide");
				djangoForm.setErrors($scope.cert_form, out_data);
			});
		}
		return false;
	};
});



app.controller("RevokeCertificateCtrl", function($scope, $http, $window, djangoUrl, djangoForm) {
	
	var success_url = $window.location.href;
	
	$scope.submit = function($event) {
		var cert_id = $($event.target).attr("data-cert-id");
		var postCertificateURL = djangoUrl.reverse("api:v1:certificate-revoke", {"pk": cert_id});
		if ($scope.cert_data) {
			$("#process-busy-modal").modal("show");
			$http.patch(postCertificateURL, $scope.cert_data).success(function(out_data) {
				$("#process-busy-modal").modal("hide");
				if (!djangoForm.setErrors($scope.cert_form, out_data.errors)) {
				    var buttons = document.getElementsByClassName("close");
				    $scope.$emit("certificate-list-updated", {});

				    for(var i = 0; i < buttons.length; i++)
				       buttons[i].click();				    
			        
				}
			}).error(function(out_data) {
				$("#process-busy-modal").modal("hide");
				djangoForm.setErrors($scope.cert_form, out_data);
			});
		}
		return false;
	};
});


app.controller("CRLFileCtrl", function($scope, $http, $window, djangoUrl, djangoForm) {
	
	var success_url = $window.location.href;
	
	$scope.submit = function($event) {
		var cert_id = $($event.target).attr("data-cert-id");
		var postCertificateURL = djangoUrl.reverse("api:v1:certificate-crl", {"pk": cert_id});
		var postCertificateFileURL = djangoUrl.reverse("api:v1:certificate-crl-file", {"pk": cert_id});

		if ($scope.cert_data) {
			$("#process-busy-modal").modal("show");
			$http.patch(postCertificateURL, $scope.cert_data).success(function(out_data) {
				$("#process-busy-modal").modal("hide");
				if (!djangoForm.setErrors($scope.cert_form, out_data.errors)) {
				    var buttons = document.getElementsByClassName("close");

				    for(var i = 0; i < buttons.length; i++)
				       buttons[i].click();
				    $("#download_iframe").attr("src",postCertificateFileURL);
				}
			}).error(function(out_data) {
				$("#process-busy-modal").modal("hide");
				djangoForm.setErrors($scope.cert_form, out_data);
			});
		}
		return false;
	};
});

