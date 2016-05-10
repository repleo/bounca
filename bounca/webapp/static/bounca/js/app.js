'use strict';

angular.module('angularDjangoRegistrationAuthApp', [
  'djng.urls',
  'ngCookies',
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'djng.forms',
]).config(function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}).config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'auth/views/main.html',
        controller: 'MainCtrl',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/register', {
        templateUrl: 'auth/views/register.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/passwordReset', {
        templateUrl: 'auth/views/passwordreset.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/passwordResetConfirm/:firstToken/:passwordResetToken', {
        templateUrl: 'auth/views/passwordresetconfirm.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/login', {
        templateUrl: 'auth/views/login.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/verifyEmail/:emailVerificationToken', {
        templateUrl: 'auth/views/verifyemail.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/logout', {
        templateUrl: 'auth/views/logout.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/userProfile', {
        templateUrl: 'auth/views/userprofile.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      })
      .when('/passwordChange', {
        templateUrl: 'auth/views/passwordchange.html',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus();
          }],
        }
      }).when('/restricted', {
          templateUrl: 'auth/views/restricted.html',
          controller: 'RestrictedCtrl',
          resolve: {
            authenticated: ['djangoAuth', function(djangoAuth){
              return djangoAuth.authenticationStatus();
            }],
          }
        })
      .when('/dashboard', {
        templateUrl: 'dashboard/views/main.html',
        controller: 'DashboardCtrl',
        resolve: {
          authenticated: ['djangoAuth', function(djangoAuth){
            return djangoAuth.authenticationStatus(true);
          }],
        }
      })
      .otherwise({
        redirectTo: '/dashboard'
      });
  })
  .run(function(djangoAuth){
    djangoAuth.initialize('/api/v1/auth', true);
  });
