from django.http.response import HttpResponse
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from Api.utils import *


class Rest(object):
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.lower()

    def enter(self, request, *args, **kwargs):
        method = request.method
        if method == 'GET':
            result = self.get(request, *args, **kwargs)
        elif method == 'POST':
            result = self.post(request, *args, **kwargs)
        elif method == 'PUT':
            result = self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            result = self.delete(request, *args, **kwargs)
        elif method == 'HEAD':
            result = self.head(request, *args, **kwargs)
        elif method == 'OPTIONS':
            result = self.options(request, *args, **kwargs)
        else:
            result = method_not_allowed()
        return result

    def get(self, request, *args, **kwargs):
        return method_not_allowed()

    def post(self, request, *args, **kwargs):
        return method_not_allowed()

    def put(self, request, *args, **kwargs):
        return method_not_allowed()

    def delete(self, request, *args, **kwargs):
        return method_not_allowed()

    def head(self, request, *args, **kwargs):
        return method_not_allowed()

    def options(self, request, *args, **kwargs):
        return method_not_allowed()


class Register(object):
    def __init__(self, version='v1'):
        self.version = version
        self.resources = []

    def regist(self, resource):
        self.resources.append(resource)

    @property
    def urls(self):
        urlpatterns = [
            url(r'^{version}/{name}$'.format(version=self.version,
                                             name=obj.name), csrf_exempt(obj.enter))
            for obj in self.resources
        ]
        return urlpatterns
