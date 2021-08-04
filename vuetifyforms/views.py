from rest_framework import exceptions
from rest_framework.views import exception_handler as drf_exception_handler


def _flatten_vue_validation(val, key_prefix=''):
    if isinstance(val, list):
        return [_flatten_vue_validation(x) for x in val]
    elif isinstance(val, dict):
        res = {}
        for k in val:
            v = _flatten_vue_validation(val[k], key_prefix=f"{k}__")
            if isinstance(v, dict):
                res.update(v)
            else:
                res[f"{key_prefix}{k}"] = val[k]
        return res
    else:
        return val


def vue_exception_handler(exc, context):
    """
    Flattens the 400 validation responses so it can be handled by vue.

    Other error are processed by the default rest_framework.views.exception_handler
        """
    if isinstance(exc, exceptions.APIException) and \
        isinstance(exc.detail, (list, dict)):
            exc.detail = _flatten_vue_validation(exc.detail)

    return drf_exception_handler(exc, context)
