from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import register_view, login_view, logout_view, UserListView, error_400, error_404, error_500
from pedidos.views import PedidosListView, PedidoCreateView, DeletadosPedidosView, import_excel_view,atualizar_pedidos
from pedidos.session_manager import SessionManager
from dash.views import ListDashView, IndicadorView
from accounts.forms import CustomPasswordResetForm
from django.conf.urls import handler400, handler404, handler500

handler400 = error_400
handler400 = error_404
handler500 = error_500

urlpatterns = [
    path('', login_view, name ='login'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name ='login'),
    path('accounts/login/', login_view, name ='login'),
    path('logout/', logout_view, name ='logout'),
    path('pedidos/', PedidosListView.as_view(), name ='pedido_list'),
    path('atualizar_pedidos/', atualizar_pedidos, name='atualizar_pedidos'),
    path('pedidos-deletados/', DeletadosPedidosView.as_view(), name='pedidos_deletados'),
    path('criar_pedido/', PedidoCreateView.as_view(), name ='pedido_create'),
    path('indicador/', IndicadorView.as_view(), name='view_indicator'),
    path('lista_indicador/', ListDashView.as_view(), name ='lista_dash'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('registrar/', register_view, name ='registro'),
    path('import/', import_excel_view, name ='import_view'),
    path('obter_progresso/', SessionManager.obter_progresso, name='obter_progresso'),
    path('limpar_progresso/', SessionManager.limpar_progresso, name='limpar_progresso'),
    path('reset_password/', 
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            html_email_template_name='password_reset_email_html.html'
        ), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]