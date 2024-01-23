from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


def register_view(request):
    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            # email = user_form.cleaned_data.get('email')
            # user = user_form.save(commit=False)
            # user.username = email
            # user.save()
            user_form.save()
            return redirect('pedido_list')
    else:
        user_form = CustomUserCreationForm()
    return render(request, 'registro.html', {'user_form': user_form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('pedido_list')
    
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('pedido_list')
        else:
            messages.error(request, 'Login não encontrado. Por favor, revise suas credenciais.')
            login_form = AuthenticationForm(request=request)
    else:
        login_form = AuthenticationForm()
    return render(request, 'login.html', {'login_form': login_form})

def logout_view(request):
    logout(request)
    return redirect('login')

class UserListView(ListView):
    model = User
    template_name = 'lista_usuario.html'
    context_object_name = 'users'

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        id = request.POST.get('user_id')

        try:
            pedido = User.objects.get(pk=id)
            pedido.save()
            pedido.delete()
        except ObjectDoesNotExist:
            return JsonResponse({'error': f'User with id {id} does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'message': 'Users deletados com sucesso'})
    
def error_400(request, exception):
    return render(request, '400.html')

def error_404(request, exception):
    return render(request, '404.html')

def error_500(request):
    return render(request, '500.html')
