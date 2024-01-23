from django.shortcuts import redirect
from .models import UrlDashBoard
from django.views.generic import ListView
from .forms import IndicatorForm
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin

# class IndicadorView(ListView):
#     model = UrlDashBoard
#     template_name = 'indicador.html'
#     context_object_name = 'indicators'

GROUP_HIERARCHY = {
    'Master': 0,
    'Gerente': 1,
    'Coordenador': 2,
    'Consultor Vendas': 3,
    'Consultor BKO': 3,
}

class IndicadorView(LoginRequiredMixin, ListView):
    model = UrlDashBoard
    template_name = 'indicador.html'
    context_object_name = 'indicators'

    def get_queryset(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)

        if 'Master' in user_groups:
            return UrlDashBoard.objects.all()
        
        accessible_indicators = UrlDashBoard.objects.filter(
            Q(group__name__in=user_groups) |
            Q(group__name='Consultor Vendas') |
            Q(group__name='Consultor BKO')
        )

        if 'Gerente' in user_groups or 'Coordenador' in user_groups:
            accessible_levels = [group for group, level in GROUP_HIERARCHY.items() if level >= GROUP_HIERARCHY['Gerente']]
            accessible_indicators = accessible_indicators.filter(group__name__in=accessible_levels)

        return accessible_indicators.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ListDashView(ListView):
    model = UrlDashBoard
    template_name = 'indicador_create.html'
    context_object_name = 'indicators'
    form_class = IndicatorForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['groups'] = Group.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if 'delete_id' in request.POST:
            delete_id = request.POST['delete_id']
            try:
                indicator = UrlDashBoard.objects.get(pk=delete_id)
                indicator.delete()
            except UrlDashBoard.DoesNotExist:
                pass
            return redirect('lista_dash')     
    
        if form.is_valid():
            form.save()
            return redirect('lista_dash')
        else:
            return self.render_to_response(self.get_context_data(form=form))
        

# class DashboardView(LoginRequiredMixin, TemplateView):
#     template_name = 'indicador.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['indicators'] = UrlDashBoard.objects.all()
#         context['user_groups'] = self.request.user.groups.values_list('id', flat=True)
#         return context
