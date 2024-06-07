# account/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied

def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type.type == 'EMPLOYEE':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view
