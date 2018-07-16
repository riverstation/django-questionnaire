import json

from Api.utils import *


def admin_required(func):
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'admin'):
            return func(self, request, *args, **kwargs)
        else:
            return not_authenticated()
    return _wrapper


def customer_required(func):
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'customer'):
            return func(self, request, *args, **kwargs)
        else:
            return not_authenticated()
    return _wrapper


def userinfo_required(func):
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'userinfo'):
            return func(self, request, *args, **kwargs)
        else:
            return not_authenticated()
    return _wrapper
