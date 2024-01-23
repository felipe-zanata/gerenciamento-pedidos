from datetime import datetime
import math
from django.forms import DateField
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from pedidos.forms import NovoPedidoForm
from pedidos.models import (DadosPedidos, DadosPedidosDeletados, Equipe, FamiliaProduto, DescricaoStatus, Produto, 
                            TipoOferta, Uf, Cargo, TipoPN, MotivoCancelamento, BkoReprovado, Observacao, Credito, TipoAgenda)
from dash.models import DescricaoStatus
from django.views.generic import ListView, CreateView
from django.db.models import Q, Sum, CharField,ForeignKey, DateTimeField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import pandas as pd
import warnings
import locale
from django.db import transaction

from pedidos.session_manager import SessionManager
from .api_status import AtualizarStatus
from .formata_import import FormatacaoValidacaoInputManual
from .formata_import_neo import FormatacaoValidacaoInputManualNeo
from django.utils import timezone

@method_decorator(login_required(login_url='login'), name='dispatch')
class PedidosListView(ListView):
    model = DadosPedidos
    template_name = 'pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 100

    def consulta_objeto(self,model: str,  nome_campo, valor_campo):
        """consulta o objeto e retorna o id correspondente"""
        try:
            filtro = {f'{nome_campo}__icontains':valor_campo}
            related_id = globals()[model].objects.get(**filtro).id
        except Exception:
            pass
    
    def get_queryset(self):
        lista = super().get_queryset()
        
        for key, value in self.request.GET.items():
            if key not in ['page']:
                if value:
                    if key == 'filtro_geral':
                        filter_query = Q()
                        for field in self.model._meta.get_fields():
                            if isinstance(field, CharField):
                                try:
                                    if field.get_internal_type() == 'DateField':
                                        filter_query |= Q(**{f'{field.name}__date': value})
                                    else:
                                        filter_query |= Q(**{f'{field.name}__icontains': value})
                                except Exception as e:
                                    print(e)
                                    pass
   
                            elif isinstance(field, DateTimeField):
                                try:
                                    dta_formatada = datetime.strptime(value, "%d/%m/%Y %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
                                    valor_data_hora = timezone.make_aware(datetime.strptime(dta_formatada, "%Y-%m-%d %H:%M:%S"))
                                    filter_query |= Q(**{f'{field.name}__date': valor_data_hora})
                                except Exception as e:
                                    print(e)
                                    pass


                            elif isinstance(field, ForeignKey):
                                try:
                                    filtro = {f'{field.name}__icontains':value}
                                    model = field.related_model.__name__
                                    related_id = globals()[model].objects.get(**filtro).id
                                    filter_query |= Q(**{f'{field.name}__id': related_id})
                                except Exception as e:
                                    pass
 

                        lista = lista.filter(filter_query)

                    try:
                        field = self.model._meta.get_field(key)
                    except:
                        continue

                    if field.is_relation and field.related_model:
                        if key == 'status':
                            n:int = 4
                        else:
                            n:int = 3
                        related_field_name = field.related_model._meta.get_fields()[n].name
    
                        related_ids = field.related_model.objects.filter(
                            Q(**{f'{related_field_name}__icontains': value})
                        ).values_list('id', flat=True)

                        lista = lista.filter(**{f'{key}__in': related_ids})  

                    else:
                        lista = lista.filter(**{f'{key}__icontains': value})

        order_column = self.request.GET.get('order_column', None)
        order_by_param = self.request.GET.get('order_by', None)

        if order_column:
            try:
                lista.model._meta.get_field(order_column)
            except Exception as e:
                order_column = 'id'

            if order_by_param == 'dsc':
                order_column = '-' + order_column
                lista = lista.order_by(order_column)
            else:
                lista = lista.order_by(order_column)

        usuario_logado = self.request.user

        if usuario_logado.is_authenticated:
            usuario = usuario_logado.username
            primeiro_nome = usuario_logado.first_name
            ultimo_nome = usuario_logado.last_name
            email = usuario_logado.email

            # //Filtrar pelo usuario ou email
            # lista = lista.filter(consultor__icontains=primeiro_nome+" "+ultimo_nome)
            # lista = lista.filter(Login_consultor__icontains=usuario)
            # lista = lista.filter(email_consultor__icontains=email)
        
        self.total_linhas = lista.count()

        return lista

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        grupos = Group.objects.filter(user=self.request.user)
        permissaoMasterGerente = any(grupo in ["Master", "Gerente"] for grupo in grupos.values_list('name', flat=True))
        permissaoNotCoordVendas = not any(grupo in ["Coordenador","Consultor Vendas"] for grupo in grupos.values_list('name', flat=True))
        permissaoNotConsultor = not any(grupo in ["Consultor BKO","Consultor Vendas"] for grupo in grupos.values_list('name', flat=True))
        permissaoNotVendas = not any(grupo in ["Consultor Vendas"] for grupo in grupos.values_list('name', flat=True))
        permissaoNotBko = not any(grupo in ["Consultor BKO"] for grupo in grupos.values_list('name', flat=True))

        usuarios = User.objects.all()
        consultores = [(str(user.id), f'{user.first_name} {user.last_name}'.strip()) for user in usuarios]
    
        locale.setlocale(locale.LC_ALL, '')
        
        try:
            total_qtd = self.object_list.aggregate(Sum('qtd'))['qtd__sum']
            total_valor = self.object_list.aggregate(Sum('valor'))['valor__sum']

            ultima_atualizacao = self.model.objects.latest('data_hora_atualizado_status').data_hora_atualizado_status
        except:
            total_qtd = 0
            total_valor = 0
            ultima_atualizacao = ''
        
        try:
            total_qtd_formatado = locale._format('%d', total_qtd, grouping=True)
        except:
            total_qtd_formatado = total_qtd
        
        try:
            total_valor_formatado = locale.currency(total_valor, grouping=True, symbol='R$')    
        except:
            total_valor_formatado = total_valor

        context['total_qtd'] = total_qtd_formatado  
        context['total_valor'] = total_valor_formatado
        context['data_hora_atualizado'] = ultima_atualizacao
        context['total_linhas'] = self.total_linhas
        
        context['grupos'] = grupos
        context['consultores'] = consultores
        context['permissaoMasterGerente'] = permissaoMasterGerente
        context['permissaoNotCoordVendas'] = permissaoNotCoordVendas
        context['permissaoNotConsultor'] = permissaoNotConsultor
        context['permissaoNotVendas'] = permissaoNotVendas
        context['permissaoNotBko'] = permissaoNotBko
        # context['bkos'] = consultores_bko
        # context['vendas'] = consultores_venda
        
        context['equipes'] = Equipe.objects.all()
        context['familia_produtos'] = FamiliaProduto.objects.all()
        context['status'] = DescricaoStatus.objects.all()
        context['produtos'] = Produto.objects.all()
        context['campanhas'] = TipoOferta.objects.all()
        context['ufs'] = Uf.objects.all()
        context['cargos'] = Cargo.objects.all()
        context['status_pns'] = TipoPN.objects.all()
        context['motivos_cancelamento'] = MotivoCancelamento.objects.all()
        context['bko_reprovados'] = BkoReprovado.objects.all() 
        context['observacoes'] = Observacao.objects.all() 
        context['creditos'] = Credito.objects.all()
        context['tipo_agendas'] = TipoAgenda.objects.all()
        
        return context
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        pedido_id = request.POST.get('pedido_id')
        pedido_ids = request.POST.getlist('pedido_ids[]',[])
        novo_valor = request.POST.get('novo_valor')
        coluna = request.POST.get('coluna')
        tipo = request.POST.get('tipo')

        if pedido_id:
            pedido = DadosPedidos.objects.get(pk=pedido_id)

        if tipo == 'deletar_pedidos':
            with transaction.atomic():
                for id in pedido_ids:
                    try:
                        pedido = DadosPedidos.objects.get(pk=int(id))
                        pedido.delete()
                    except ObjectDoesNotExist:
                        return JsonResponse({'error': f'Pedido with id {id} does not exist'}, status=400)
                    except Exception as e:
                        print(e)
                        return JsonResponse({'error': str(e)}, status=500)

            # If all deletions are successful, send back a success response
            return JsonResponse({'message': 'Pedidos deletados com sucesso'})

        elif hasattr(pedido, coluna) and hasattr(getattr(pedido, coluna), 'id'):

            try:
                campo_relacionado = pedido._meta.get_field(coluna)
                relacionado_modelo = campo_relacionado.related_model
                relacionado_modelo_instancia, _ = relacionado_modelo.objects.get_or_create(id=novo_valor)

                setattr(pedido, coluna, relacionado_modelo_instancia)

                pedido.save()
            except ValidationError as ve:
                return JsonResponse({'error': str(ve)}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

            return JsonResponse({'message': 'Atualização bem-sucedida'})
        elif hasattr(pedido, coluna):
            
            try:
                setattr(pedido, coluna, novo_valor)

                pedido.save()
            except ValidationError as ve:
                return JsonResponse({'error': str(ve)}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
            
            return JsonResponse({'message': 'Atualização bem-sucedida'})
        else:
            return JsonResponse({'message': 'Coluna inválida ou não é uma chave estrangeira'}, status=400)

@method_decorator(login_required(login_url='login'), name='dispatch')
class DeletadosPedidosView(ListView):
    model = DadosPedidosDeletados
    template_name = 'pedido_delete.html'
    context_object_name = 'pedidos_deletados'
    paginate_by = 500

    def get_queryset(self):
        lista = super().get_queryset()

        for key, value in self.request.GET.items():
            if key not in ['page']:
                if value:

                    if key == 'filtro_geral':
                        filter_query = Q()
                        for field in self.model._meta.get_fields():
                            if isinstance(field, CharField):
                                try:
                                    if field.get_internal_type() == 'DateField':
                                        filter_query |= Q(**{f'{field.name}__date': value})
                                    else:
                                        filter_query |= Q(**{f'{field.name}__icontains': value})
                                except Exception as e:
                                    print(e)
                                    pass
   
                            elif isinstance(field, DateTimeField):
                                try:
                                    dta_formatada = datetime.strptime(value, "%d/%m/%Y %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')
                                    valor_data_hora = timezone.make_aware(datetime.strptime(dta_formatada, "%Y-%m-%d %H:%M:%S"))
                                    filter_query |= Q(**{f'{field.name}__date': valor_data_hora})
                                except Exception as e:
                                    print(e)
                                    pass


                            elif isinstance(field, ForeignKey):
                                try:
                                    filtro = {f'{field.name}__icontains':value}
                                    model = field.related_model.__name__
                                    related_id = globals()[model].objects.get(**filtro).id
                                    filter_query |= Q(**{f'{field.name}__id': related_id})
                                except Exception as e:
                                    pass
 

                        lista = lista.filter(filter_query)

                    try:
                        field = self.model._meta.get_field(key)
                    except:
                        continue

                    if field.is_relation and field.related_model:

                        if key == 'status':
                            n:int = 4
                        else:
                            n:int = 3
                        related_field_name = field.related_model._meta.get_fields()[n].name
    
                        related_ids = field.related_model.objects.filter(
                            Q(**{f'{related_field_name}__icontains': value})
                        ).values_list('id', flat=True)

                        lista = lista.filter(**{f'{key}__in': related_ids})  

                    else:
                        lista = lista.filter(**{f'{key}__icontains': value})

        return lista
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        pedido_ids = request.POST.getlist('pedido_ids[]',[])
        salvar: bool = request.POST.get('salvar') == 'true'

        with transaction.atomic():
            for id in pedido_ids:
                try:
                    pedido = DadosPedidosDeletados.objects.get(pk=id)
                    pedido._salvar = salvar
                    pedido.save()
                    pedido.delete()
                except ObjectDoesNotExist:
                    return JsonResponse({'error': f'Pedido with id {id} does not exist'}, status=400)
                except Exception as e:
                    print(e)
                    return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'message': 'Pedidos deletados com sucesso'})

@method_decorator(login_required(login_url='login'), name='dispatch')
class PedidoCreateView(CreateView):
    model = DadosPedidos
    form_class = NovoPedidoForm
    template_name = 'pedido_create.html'
    success_url = '/pedidos/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuarios = User.objects.all()
        consultores = [(str(user.id), f'{user.first_name} {user.last_name}'.strip()) for user in usuarios]

        context['consultores'] = consultores
        return context

    def form_valid(self, form):
        form.instance.email_usuario = self.request.user.email
        form.instance.login_usuario = self.request.user.username
        return super().form_valid(form)

@csrf_exempt
def atualizar_pedidos(request):
    try:
        atualizar = AtualizarStatus()
        atualizar.atualizar_pedidos()

        return JsonResponse({'success': True, 'message': 'Pedidos atualizados com sucesso.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def import_excel_view(request):
    request.session.pop('data', None)
    request.session.save()
    if request.method == 'POST':
        SessionManager.salvar_dados(request, "Iniciando leitura de dados", "Concluído", 4)
        try:
            excel_file = request.FILES['excel_file']
            warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

            if str(excel_file).endswith('.xlsx'):
                df = pd.read_excel(excel_file, engine='openpyxl', parse_dates=False)

            elif str(excel_file).endswith('.csv'):
                df = pd.read_csv(excel_file, sep=';', encoding='latin-1')
            else:
                e='Formato de arquivo não suportado'
                error_data = error_data_msg(e)
                return render(request, 'importar_excel.html', {'error_message': [error_data]})
        except Exception as e:
            error_data = error_data_msg(e)
            return render(request, 'importar_excel.html', {'error_message': [error_data]})
        
        SessionManager.salvar_dados(request, "Leitura de dados realizada", "Concluído", 8)
        
        try:   
            tipo_import = request.POST.get('tipo_data')
            if tipo_import == 'neo_crm':
                valida = FormatacaoValidacaoInputManualNeo(df, request)
                df_formatado, msg = valida.validacao_df()
            else:
                valida = FormatacaoValidacaoInputManual(df, request)
                df_formatado, msg = valida.validacao_df()

            if msg != 'OK':
                error_data = error_data_msg(msg)
                return render(request, 'importar_excel.html', {'error_message': [error_data]})

            with transaction.atomic():
                for _, row in df_formatado.iterrows():
                    acao_registro(request, row, tipo_import)

            SessionManager.salvar_dados(request, "Dados importados e gravados no banco de dados", "Concluído", 100)
                    
            return JsonResponse({'success': True})
        except Exception as e:
            SessionManager.salvar_dados(request, str(e), "Concluído", 100)
            error_data = error_data_msg(e)
            return render(request, 'importar_excel.html', {'error_message': [error_data]})

    else:
        return render(request, 'importar_excel.html')

def error_data_msg(erro):
    error_data = {
                'data': datetime.now(),
                'logger': str(erro), 
                'status': 'Erro'
            }
    return error_data

def converter_para_float(valor):
    try:
        return locale.atof(valor.replace('R$', ''))
    except ValueError:
        return 0
    
@transaction.atomic   
def atualizar_registro_neo(request, dados: pd.Series):
    try:
        nome_usuario = request.user.username
        email_usuario = request.user.email
        dados = dados.where(dados.notnull(), None)

        equipe_instancia = Equipe.objects.get(id=dados.EQUIPE)
        status_instancia = DescricaoStatus.objects.get(id=dados.ETAPA)

        resultado = DadosPedidos.objects.filter(atividade = dados.NUMERO).order_by('carimbo_data_hora').first()

        resultado.equipe = equipe_instancia
        resultado.status = status_instancia
        resultado.cnpj = dados['CPF-CNPJ']
        resultado.login_usuario = nome_usuario
        resultado.email_usuario = email_usuario
        resultado.save()
    except Exception as e:
        SessionManager.salvar_dados(request, str(e), "Concluído", 100)
        raise Exception(e)
    
def atualizar_registro(request, dados: pd.Series):
    try:
        nome_usuario = request.user.username
        email_usuario = request.user.email
        dados = dados.where(dados.notnull(), None)

        # consultor_instancia = User.objects.get(id=dados.CONSULTOR)
        equipe_instancia = Equipe.objects.get(id=dados.EQUIPE)
        familia_instancia = FamiliaProduto.objects.get(id=dados['FAMÍLIA DE PRODUTOS'])
        motivo_instancia = MotivoCancelamento.objects.get(id=dados['MOTIVO CANCELAMENTO'])
        bko_rep_instancia = BkoReprovado.objects.get(id=dados['BKO REPROVADO'])
        tipo_agenda_instancia = TipoAgenda.objects.get(id=dados['TIPO AGENDA'])
        status_instancia = DescricaoStatus.objects.get(id=dados.STATUS)
        produto_instancia = Produto.objects.get(id=dados.PRODUTO)
        oferta_instancia = TipoOferta.objects.get(id=dados.CAMPANHA)
        uf_instancia = Uf.objects.get(id=1)
        cargo_instancia = Cargo.objects.get(id=dados.CARGO)
        pn_instancia = TipoPN.objects.get(id=dados['STATUS PN'])
        credito_instancia = Credito.objects.get(id=dados['CRÉDITO'])
        Observacao_instancia_1 = Observacao.objects.get(id=dados['OBSERVAÇÃO 1'])
        Observacao_instancia_2 = Observacao.objects.get(id=dados['OBSERVAÇÃO 2'])


        resultado = DadosPedidos.objects.get(pk = dados.ID)
        # resultado = DadosPedidos.objects.filter(pk = dados.ID).order_by('carimbo_data_hora').first()
        # resultado.carimbo_data_hora = dados['CARIMBO DATA/HORA']
        # if str(dados['CARIMBO DATA/HORA']) in ['None',None,'', 'nan']:
        #     formato_js = datetime.now()
        #     data_hora = formato_js.strftime("%Y/%m/%d %H:%M:%S")
        # else:
        #     data_hora = dados['CARIMBO DATA/HORA']
        if not int(dados.EQUIPE) == 5:
            resultado.equipe = equipe_instancia
        if not str(dados.CONSULTOR) in ['None', None, '', 'nan']:
            resultado.consultor = dados.CONSULTOR
        if not int(dados.CARGO) == 5:
            resultado.cargo = cargo_instancia
        if not str(dados.DATA) in ['None', None, '', 'nan']:
            resultado.data = dados.DATA
        if not str(dados.ATIVIDADE) in ['None', None, '', 'nan']:
            resultado.atividade = dados.ATIVIDADE
        if not str(dados.CNPJ) in ['None', None, '', 'nan']:
            resultado.cnpj = dados.CNPJ
        if not str(dados['RAZÃO SOCIAL']) in ['None', None, '', 'nan']:
            resultado.razao_social = dados['RAZÃO SOCIAL']
        if not int(dados['FAMÍLIA DE PRODUTOS']) == 1:
            resultado.familia_produto = familia_instancia
        if not int(dados.STATUS) == 1:
            resultado.status = status_instancia
        if not int(dados['STATUS PN']) == 12:
            resultado.status_pn = pn_instancia
        if not int(dados.PRODUTO) == 1:
            resultado.produto = produto_instancia
        if not str(dados.QTDE) in ['None', None, '', 'nan']:
            resultado.qtd = dados.QTDE
        if not str(dados.VALOR) in ['None', None, '', 'nan']:
            resultado.valor = float(str(dados.VALOR).replace(',','.'))
        if not int(dados['MOTIVO CANCELAMENTO']) == 1:
            resultado.motivo_cancelamento = motivo_instancia
        if not str(dados['SIMULAÇÃO']) in ['None', None, '', 'nan']:
            resultado.simulacao = dados['SIMULAÇÃO']
        if not str(dados['COTAÇÃO']) in ['None', None, '', 'nan']:
            resultado.cotacao = dados['COTAÇÃO']
        if not str(dados.PEDIDO) in ['None', None, '', 'nan']:
            resultado.pedido = dados.PEDIDO
        if not int(dados['CRÉDITO']) == 1:
            resultado.credito = credito_instancia
        if not int(dados['BKO REPROVADO']) == 1:
            resultado.bko_reprovado = bko_rep_instancia
        if not str(dados['DATA ATIVAÇÃO']) in ['None', None, '', 'nan']:
            resultado.data_ativacao = dados['DATA ATIVAÇÃO']
        if not int(dados['TIPO AGENDA']) == 1:
            resultado.tipo_agenda = tipo_agenda_instancia
        if not str(dados['DATA AGENDA']) in ['None', None, '', 'nan']:        
            resultado.data_agenda = dados['DATA AGENDA']
        if not str(dados['HORA AGENDA']) in ['None', None, '', 'nan']:                 
            resultado.hora_agenda = dados['HORA AGENDA']
        if not int(dados.CAMPANHA) == 1:
            resultado.campanha = oferta_instancia
        if not str(dados['DATA CAMPANHA']) in ['None', None, '', 'nan']:                 
            resultado.data_campanha = dados['DATA CAMPANHA']
        if not str(dados['DATA CAMPANHA']) in ['None', None, '', 'nan']:
            resultado.nome_gestor = dados['NOME GESTOR']
        if not str(dados['CELULAR GESTOR']) in ['None', None, '', 'nan']:
            resultado.celular_gestor = dados['CELULAR GESTOR']
        if not str(dados['E-MAIL GESTOR']) in ['None', None, '', 'nan']:
            resultado.email_gestor = dados['E-MAIL GESTOR']
        if not int(dados['OBSERVAÇÃO 1']) == 1:
            resultado.observacao_1 = Observacao_instancia_1 
        if not int(dados['OBSERVAÇÃO 2']) == 1:
            resultado.observacao_2 = Observacao_instancia_2
        if not str(dados['DATA CQV']) in ['None', None, '', 'nan']:
            resultado.data_cqv = dados['DATA CQV']
        if not str(dados['BKO CQV']) in ['None', None, '', 'nan']:
            resultado.bko_cqv = dados['BKO CQV']
        # resultado.data_criacao = dados['DATA CRIAÇÃO']
        if not str(dados['BKO CRIAÇÃO']) in ['None', None, '', 'nan']:
            resultado.bko_criacao = dados['BKO CRIAÇÃO']
        if not str(dados['DATA ACEITE']) in ['None', None, '', 'nan']:
            resultado.data_aceite = dados['DATA ACEITE']
        if not str(dados['BKO ACEITE']) in ['None', None, '', 'nan']:
            resultado.bko_aceite =  dados['BKO ACEITE']
        if not str(dados['DATA INPUT']) in ['None', None, '', 'nan']:
            resultado.data_input = dados['DATA INPUT']
        if not str(dados['BKO INPUT']) in ['None', None, '', 'nan']:
            resultado.bko_input = dados['BKO INPUT']
        if not str(dados['DATA PN SALVO']) in ['None', None, '', 'nan']:
            resultado.data_pn_salvo = dados['DATA PN SALVO']
        if not str(dados['PN SALVO']) in ['None', None, '', 'nan']:
            resultado.pn_salvo = dados['PN SALVO']
        resultado.uf = uf_instancia
        resultado.login_usuario = nome_usuario
        resultado.email_usuario = email_usuario
        # resultado.data_hora_atualizado_status = datetime.now()
        resultado.save()
        # resultado = None
    except Exception as e:
        SessionManager.salvar_dados(request, str(e), "Concluído", 100)
        raise Exception(e)

@transaction.atomic
def inserir_registro(request, dados: pd.Series):
    try:
        nome_usuario = request.user.username
        email_usuario = request.user.email
        # ipdb.set_trace()

        # consultor_instancia = User.objects.get(id=dados.CONSULTOR)
        equipe_instancia = Equipe.objects.get(id=dados.EQUIPE)
        familia_instancia = FamiliaProduto.objects.get(id=dados['FAMÍLIA DE PRODUTOS'])
        motivo_instancia = MotivoCancelamento.objects.get(id=dados['MOTIVO CANCELAMENTO'])
        bko_rep_instancia = BkoReprovado.objects.get(id=dados['BKO REPROVADO'])
        tipo_agenda_instancia = TipoAgenda.objects.get(id=dados['TIPO AGENDA'])
        status_instancia = DescricaoStatus.objects.get(id=dados.STATUS)
        produto_instancia = Produto.objects.get(id=dados.PRODUTO)
        oferta_instancia = TipoOferta.objects.get(id=dados.CAMPANHA)
        uf_instancia = Uf.objects.get(id=1)
        cargo_instancia = Cargo.objects.get(id=dados.CARGO)
        pn_instancia = TipoPN.objects.get(id=dados['STATUS PN'])
        credito_instancia = Credito.objects.get(id=dados['CRÉDITO'])
        Observacao_instancia_1 = Observacao.objects.get(id=dados['OBSERVAÇÃO 1'])
        Observacao_instancia_2 = Observacao.objects.get(id=dados['OBSERVAÇÃO 2'])

        # bko_criacao_instancia = User.objects.get(id=dados['BKO CRIAÇÃO'])
        # bko_aceite_instancia = User.objects.get(id=dados['BKO ACEITE'])
        # bko_input_instancia = User.objects.get(id=dados['BKO INPUT'])

        dados = dados.where(dados.notnull(), None)
        # dados['CARIMBO DATA/HORA'] = pd.to_datetime(dados['CARIMBO DATA/HORA'], format='%d/%m/%Y %H:%M:S', errors='coerce')
        DadosPedidos.objects.create(
        # id = dados['ID'], 
        carimbo_data_hora = dados['CARIMBO DATA/HORA'], 
        equipe = equipe_instancia, 
        consultor = dados.CONSULTOR , 
        cargo = cargo_instancia,
        data = dados.DATA, 
        atividade = dados.ATIVIDADE, 
        cnpj = dados.CNPJ, 
        razao_social = dados['RAZÃO SOCIAL'], 
        familia_produto = familia_instancia, 
        status = status_instancia, 
        status_pn = pn_instancia, 
        produto = produto_instancia, 
        qtd = dados.QTDE, 
        valor = float(str(dados.VALOR).replace(',','.')), 
        motivo_cancelamento = motivo_instancia, 
        simulacao = dados['SIMULAÇÃO'], 
        cotacao = dados['COTAÇÃO'], 
        pedido = dados.PEDIDO, 
        credito = credito_instancia, 
        bko_reprovado = bko_rep_instancia, 
        data_ativacao = dados['DATA ATIVAÇÃO'], 
        tipo_agenda = tipo_agenda_instancia, 
        data_agenda = dados['DATA AGENDA'], 
        hora_agenda = dados['HORA AGENDA'], 
        campanha = oferta_instancia, 
        data_campanha = dados['DATA CAMPANHA'], 
        nome_gestor = dados['NOME GESTOR'], 
        celular_gestor = dados['CELULAR GESTOR'], 
        email_gestor = dados['E-MAIL GESTOR'], 
        observacao_1 = Observacao_instancia_1,  
        observacao_2 = Observacao_instancia_2, 
        data_cqv = dados['DATA CQV'], 
        bko_cqv = dados['BKO CQV'], 
        data_criacao = dados['DATA CRIAÇÃO'], 
        bko_criacao = dados['BKO CRIAÇÃO'], 
        data_aceite = dados['DATA ACEITE'], 
        bko_aceite = dados['BKO ACEITE'],  
        data_input = dados['DATA INPUT'], 
        bko_input = dados['BKO INPUT'], 
        data_pn_salvo = dados['DATA PN SALVO'], 
        pn_salvo = dados['PN SALVO'], 
        uf = uf_instancia, 
        login_usuario = nome_usuario, 
        email_usuario = email_usuario, 
        # data_hora_atualizado_status = datetime.strptime(datetime.now(), "%Y-%m-%d %H:%M"), 
        )
    except Exception as e:
        print(e)
        SessionManager.salvar_dados(request, str(e), "Concluído", 100)
        raise Exception(e)
    
def acao_registro(request, dado: pd.Series, tipo_import: str):
    """verifica qual tipo de ação deve ser tomado com os arquivos importados"""
    try:
        if tipo_import == 'neo_crm':
            atividade_loc = dado.NUMERO

            resultado = DadosPedidos.objects.filter(atividade = atividade_loc).order_by('carimbo_data_hora').first()
            if resultado:
                atualizar_registro_neo(request, dado)
        else:
            atividade_loc = dado.ID

            if (isinstance(atividade_loc, int) or isinstance(atividade_loc, float)) and not math.isnan(atividade_loc):

                resultado = DadosPedidos.objects.filter(pk = int(atividade_loc))
                if resultado:
                    atualizar_registro(request, dado)
                else:
                    inserir_registro(request, dado)
            else:
                inserir_registro(request, dado)

    except Exception as e:
        SessionManager.salvar_dados(request, str(e), "Concluído", 100)
        raise Exception(e)
