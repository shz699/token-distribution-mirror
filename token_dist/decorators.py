from django.shortcuts import redirect

def admin_access(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_admin:
                return redirect('dashboard')
        else:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
