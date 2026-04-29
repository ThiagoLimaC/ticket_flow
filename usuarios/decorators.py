from functools import wraps
from django.shortcuts import redirect


def requer_perfil(*tipos):
    """
    Decorator que restringe acesso a views por tipo de perfil.
    Uso: @requer_perfil('admin') ou @requer_perfil('admin', 'tecnico')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # usuário não autenticado vai para o login
            if not request.user.is_authenticated:
                return redirect('login')

            # usuário autenticado mas sem o perfil permitido vai para o dashboard
            if request.user.perfil.tipo not in tipos:
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator