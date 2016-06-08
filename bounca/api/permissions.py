__author__ = "Jeroen Arnoldus"
__copyright__ = "Copyright 2016, Repleo, Amstelveen"
__credits__ = ["Jeroen Arnoldus"]
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Jeroen Arnoldus"
__email__ = "jeroen@repleo.nl"
__status__ = "Production"

from rest_framework import permissions


class MyUserPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_admin
        elif view.action == 'retrieve':
            return True
        else:
            return False


    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_admin or obj == request.user                                                                       
        else:                                                                              
            return False
