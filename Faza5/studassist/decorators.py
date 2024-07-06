# Zlatko Golubović 0089/2021
from django.http import HttpResponseForbidden

def group_required(groups=[]):
    """
    Decorator for views that checks whether the user is a member of any of the specified groups.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("403 Zabranjeno: Nemate dozvolu da pristupate ovoj stranici.")
        return _wrapped_view
    return decorator