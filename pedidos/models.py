from django.db import models
from dash.models import DescricaoStatus
from django.contrib.auth.models import User, Group
from django.utils import timezone


class Cargo(models.Model):
    id = models.AutoField(primary_key=True)
    cargo = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.cargo

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

class Produto(models.Model):
    id = models.AutoField(primary_key=True)
    produto = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.produto

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

class TipoOferta(models.Model):
    id = models.AutoField(primary_key=True)
    oferta = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.oferta

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'

class Equipe(models.Model):
    id = models.AutoField(primary_key=True)
    equipe = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.equipe

    class Meta:
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'

class Uf(models.Model):
    id = models.AutoField(primary_key=True)
    uf = models.CharField(max_length=10, blank=False, null=False)

    def __str__(self):
        return self.uf

    class Meta:
        verbose_name = 'UF'
        verbose_name_plural = 'UF'

class FamiliaProduto(models.Model):
    id = models.AutoField(primary_key=True)
    familia_produto = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.familia_produto

    class Meta:
        verbose_name = 'Familia Produto'
        verbose_name_plural = 'Familia Produtos'

class TipoPN(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_PN = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.tipo_PN

    class Meta:
        verbose_name = 'PN'
        verbose_name_plural = 'PN'

class MotivoCancelamento(models.Model):
    motivo_cancelamento = models.CharField(max_length=255, blank = True, null=True)
    
    def __str__(self):
        return self.motivo_cancelamento

    class Meta:
        verbose_name = 'Motivo Cancelamento'
        verbose_name_plural = 'Motivo Cancelamento'

class BkoReprovado(models.Model):
    bko_reprovado = models.CharField(max_length=255, blank = True, null=True)

    def __str__(self):
        return self.bko_reprovado

    class Meta:
        verbose_name = 'BKO Reprovado'
        verbose_name_plural = 'BKO Reprovados'

class TipoAgenda(models.Model):
    tipo_agenda = models.CharField(max_length=255, blank = True, null=True)

    def __str__(self):
        return self.tipo_agenda

    class Meta:
        verbose_name = 'Tipo Agenda'
        verbose_name_plural = 'Tipo Agenda'

class Observacao(models.Model):
    observacao = models.CharField(max_length=255, blank = True, null=True)

    def __str__(self):
        return self.observacao

    class Meta:
        verbose_name = 'Observação'
        verbose_name_plural = 'Observações'

class Consultor(models.Model):

    @classmethod
    def carregar_usuarios(cls, grupo = ''):
        """filtra os usuario de acordo com o grupo"""
        usuarios = []
        usuarios_listados = []

        if grupo:
            # usuarios =  User.objects.filter(groups__name=grupo)
            grupo_objeto = Group.objects.get(name=grupo)
            usuarios = grupo_objeto.user_set.all()
        else:
            usuarios = User.objects.all()

        for user in usuarios:
            # nome_usuario = f'{user.first_name} {user.last_name}'
            # usuarios_listados.append((nome_usuario, nome_usuario))
            nome_usuario = f'{user.first_name} {user.last_name}'.strip()
            usuarios_listados.append((str(user.id), nome_usuario))  # Note a mudança aqui

        return usuarios_listados


    def __str__(self):
        return self.consultor

    class Meta:
        verbose_name = 'Consultor'
        verbose_name_plural = 'Consultores'

class Credito(models.Model):
    credito = models.CharField(max_length=255, blank = True, null=True)

    def __str__(self):
        return self.credito

    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Créditos'

class DadosPedidos(models.Model):
    id = models.AutoField(primary_key=True)
    carimbo_data_hora = models.DateTimeField(default=timezone.now)
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT, related_name='equipe_fk')
    consultor = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='cargo_fk')
    data = models.DateField(blank=True, null=True)
    atividade = models.IntegerField(blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    familia_produto = models.ForeignKey(FamiliaProduto, on_delete=models.PROTECT, related_name='familia_produto_fk')
    status = models.ForeignKey(DescricaoStatus, on_delete=models.PROTECT, related_name= 'status')
    status_pn = models.ForeignKey(TipoPN, on_delete=models.PROTECT, null=True, blank=True, related_name='status_pn')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='produto_pk')
    qtd = models.IntegerField(blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)
    motivo_cancelamento = models.ForeignKey(MotivoCancelamento, on_delete=models.CASCADE, default=1)
    simulacao = models.IntegerField(blank=True, null=True)
    cotacao = models.CharField(max_length=100, blank=True, null=True)
    pedido = models.CharField(max_length=255, blank=True, null=True)
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE)
    bko_reprovado = models.ForeignKey(BkoReprovado, on_delete=models.CASCADE, related_name='bko_rep')
    data_ativacao = models.DateField(blank=True, null=True)
    tipo_agenda = models.ForeignKey(TipoAgenda, on_delete=models.CASCADE, related_name='tip_agenda')
    data_agenda = models.DateField(blank=True, null=True)
    hora_agenda = models.TimeField(blank=True, null=True)
    campanha = models.ForeignKey(TipoOferta, on_delete=models.PROTECT, related_name='oferta_pk')
    data_campanha = models.DateField(blank=True, null=True)
    nome_gestor = models.CharField(max_length=255, blank=True, null=True)
    celular_gestor = models.CharField(max_length=20, blank=True, null=True)
    email_gestor = models.EmailField(max_length=255, blank=True, null=True) 
    observacao_1 = models.ForeignKey(Observacao, on_delete=models.PROTECT, related_name='obs_1')
    observacao_2 = models.ForeignKey(Observacao, on_delete=models.PROTECT, related_name='obs_2')
    data_cqv = models.DateField(blank=True, null=True)
    bko_cqv = models.CharField(max_length=255, blank=True, null=True) 
    data_criacao = models.DateField(blank=True, null=True)
    bko_criacao = models.CharField(max_length=255,  blank=True, null=True)
    data_aceite = models.DateField(blank=True, null=True)
    bko_aceite = models.CharField(max_length=255,  blank=True, null=True) 
    data_input = models.DateField(blank=True, null=True)
    bko_input = models.CharField(max_length=255,  blank=True, null=True) 
    data_pn_salvo = models.DateField(blank=True, null=True)
    pn_salvo = models.CharField(max_length=255,  blank=True, null=True)
    uf = models.ForeignKey(Uf, on_delete=models.PROTECT, related_name='uf_fk')
    login_usuario = models.CharField(max_length=255, blank=True, null=True)
    email_usuario = models.EmailField(max_length=255, blank=True, null=True)
    data_hora_atualizado_status = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.atividade
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Dado Pedido'
        verbose_name_plural = 'Dado Pedidos'

class DadosPedidosDeletados(models.Model):
    data_exclusao = models.DateTimeField(auto_now_add=True)
    carimbo_data_hora = models.DateTimeField(auto_now_add=False)
    equipe = models.ForeignKey(Equipe, 
                               on_delete=models.PROTECT,
                               blank=True, 
                               null=True, 
                               related_name='equipe_fk_delete')
    consultor = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.ForeignKey(Cargo, 
                              on_delete=models.PROTECT,
                              blank=True, 
                              null=True, 
                              related_name='cargo_fk_delete')
    data = models.DateField(blank=True, null=True)
    atividade = models.IntegerField(blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    razao_social = models.CharField(max_length=255, blank=True, null=True)
    familia_produto = models.ForeignKey(FamiliaProduto, 
                                        on_delete=models.PROTECT,
                                        blank=True, 
                                        null=True, 
                                        related_name='familia_produto_fk_delete')
    status = models.ForeignKey(DescricaoStatus, 
                               on_delete=models.PROTECT, 
                               related_name= 'status_delete')
    status_pn = models.ForeignKey(TipoPN, 
                                  on_delete=models.PROTECT, 
                                  null=True, 
                                  blank=True, 
                                  related_name='status_pn_delete')
    produto = models.ForeignKey(Produto, 
                                on_delete=models.PROTECT,
                                blank=True, 
                                null=True, 
                                related_name='produto_pk_delete')
    qtd = models.IntegerField(blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)
    motivo_cancelamento = models.ForeignKey(MotivoCancelamento, 
                                            on_delete=models.CASCADE, 
                                            blank=True, 
                                            null=True)
    simulacao = models.IntegerField(blank=True, null=True)
    cotacao = models.CharField(max_length=100, blank=True, null=True)
    pedido = models.CharField(max_length=255, blank=True, null=True)
    credito = models.ForeignKey(Credito, 
                                on_delete=models.CASCADE, 
                                blank=True, null=True)
    bko_reprovado = models.ForeignKey(BkoReprovado, 
                                      on_delete=models.CASCADE,
                                      blank=True, 
                                      null=True, 
                                      related_name='bko_rep_delete')
    data_ativacao = models.DateField(blank=True, null=True)
    tipo_agenda = models.ForeignKey(TipoAgenda, 
                                    on_delete=models.CASCADE,
                                    blank=True, 
                                    null=True, 
                                    related_name='tip_agenda_delete')
    data_agenda = models.DateField(blank=True, null=True)
    hora_agenda = models.TimeField(blank=True, null=True)
    campanha = models.ForeignKey(TipoOferta, 
                                 on_delete=models.PROTECT,
                                 blank=True, 
                                 null=True, 
                                 related_name='oferta_pk_delete')
    data_campanha = models.DateField(blank=True, null=True)
    nome_gestor = models.CharField(max_length=255, blank=True, null=True)
    celular_gestor = models.CharField(max_length=20, blank=True, null=True)
    email_gestor = models.EmailField(max_length=255, blank=True, null=True)
    observacao_1 = models.ForeignKey(Observacao, 
                                     on_delete=models.PROTECT,
                                     blank=True, 
                                     null=True, 
                                     related_name='obs_1_delete') 
    observacao_2 = models.ForeignKey(Observacao, 
                                     on_delete=models.PROTECT,
                                     blank=True, 
                                     null=True, 
                                     related_name='obs_2_delete')
    data_cqv = models.DateField(blank=True, null=True)
    bko_cqv = models.CharField(max_length=255, blank=True, null=True)
    data_criacao = models.DateField(blank=True, null=True)
    bko_criacao = models.CharField(max_length=255, blank=True, null=True)
    data_aceite = models.DateField(blank=True, null=True)
    bko_aceite = models.CharField(max_length=255, blank=True, null=True) 
    data_input = models.DateField(blank=True, null=True)
    bko_input = models.CharField(max_length=255, blank=True, null=True)
    data_pn_salvo = models.DateField(blank=True, null=True)
    pn_salvo = models.CharField(max_length=255, blank=True, null=True)
    uf = models.ForeignKey(Uf, 
                           on_delete=models.PROTECT, 
                           related_name='uf_fk_delete')
    login_usuario = models.CharField(max_length=255, blank=True, null=True)
    email_usuario = models.EmailField(max_length=255, blank=True, null=True)
    data_hora_atualizado_status = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.atividade
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Pedido Deletado'
        verbose_name_plural = 'Pedidos Deletados'