from datetime import datetime, timezone
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from pedidos.models import DadosPedidos, DadosPedidosDeletados
from django.utils import timezone
@receiver(post_delete, sender=DadosPedidos)
def pedido_deletados(sender, instance, **kwargs):
    
    if instance.carimbo_data_hora is None:
        instance.carimbo_data_hora = timezone.now

    print('####### dados deletados em tabela temporaria #####')
    DadosPedidosDeletados.objects.create(
    carimbo_data_hora = instance.carimbo_data_hora, 
    equipe = instance.equipe, 
    consultor = instance.consultor, 
    cargo = instance.cargo,
    data = instance.data, 
    atividade = instance.atividade, 
    cnpj = instance.cnpj, 
    razao_social = instance.razao_social, 
    familia_produto = instance.familia_produto, 
    status = instance.status, 
    status_pn = instance.status_pn, 
    produto = instance.produto, 
    qtd = instance.qtd, 
    valor = instance.valor, 
    motivo_cancelamento = instance.motivo_cancelamento, 
    simulacao = instance.simulacao, 
    cotacao = instance.cotacao, 
    pedido = instance.pedido, 
    credito = instance.credito, 
    bko_reprovado = instance.bko_reprovado, 
    data_ativacao = instance.data_ativacao, 
    tipo_agenda = instance.tipo_agenda, 
    data_agenda = instance.data_agenda, 
    hora_agenda = instance.hora_agenda, 
    campanha = instance.campanha, 
    data_campanha = instance.data_campanha, 
    nome_gestor = instance.nome_gestor, 
    celular_gestor = instance.celular_gestor, 
    email_gestor = instance.email_gestor, 
    observacao_1 = instance.observacao_1,  
    observacao_2 = instance.observacao_2, 
    data_cqv = instance.data_cqv, 
    bko_cqv = instance.bko_cqv, 
    data_criacao = instance.data_criacao, 
    bko_criacao = instance.bko_criacao, 
    data_aceite = instance.data_aceite, 
    bko_aceite = instance.bko_aceite,  
    data_input = instance.data_input, 
    bko_input = instance.bko_input, 
    data_pn_salvo = instance.data_pn_salvo, 
    pn_salvo = instance.pn_salvo, 
    uf = instance.uf, 
    login_usuario = instance.login_usuario, 
    email_usuario = instance.email_usuario, 
    data_hora_atualizado_status = instance.data_hora_atualizado_status, 
    )

@receiver(post_delete, sender=DadosPedidosDeletados)
def restaurar_deletados(sender, instance, **kwargs):
    if instance._salvar:
        if instance.carimbo_data_hora is None:
            instance.carimbo_data_hora = timezone.now
        print('####### Retornando os dados para tabela original #####')
        DadosPedidos.objects.create(
            carimbo_data_hora = instance.carimbo_data_hora, 
            equipe = instance.equipe, 
            consultor = instance.consultor, 
            cargo = instance.cargo,
            data = instance.data, 
            atividade = instance.atividade, 
            cnpj = instance.cnpj, 
            razao_social = instance.razao_social, 
            familia_produto = instance.familia_produto, 
            status = instance.status, 
            status_pn = instance.status_pn, 
            produto = instance.produto, 
            qtd = instance.qtd, 
            valor = instance.valor, 
            motivo_cancelamento = instance.motivo_cancelamento, 
            simulacao = instance.simulacao, 
            cotacao = instance.cotacao, 
            pedido = instance.pedido, 
            credito = instance.credito, 
            bko_reprovado = instance.bko_reprovado, 
            data_ativacao = instance.data_ativacao, 
            tipo_agenda = instance.tipo_agenda, 
            data_agenda = instance.data_agenda, 
            hora_agenda = instance.hora_agenda, 
            campanha = instance.campanha, 
            data_campanha = instance.data_campanha, 
            nome_gestor = instance.nome_gestor, 
            celular_gestor = instance.celular_gestor, 
            email_gestor = instance.email_gestor, 
            observacao_1 = instance.observacao_1,  
            observacao_2 = instance.observacao_2, 
            data_cqv = instance.data_cqv, 
            bko_cqv = instance.bko_cqv, 
            data_criacao = instance.data_criacao, 
            bko_criacao = instance.bko_criacao, 
            data_aceite = instance.data_aceite, 
            bko_aceite = instance.bko_aceite,  
            data_input = instance.data_input, 
            bko_input = instance.bko_input, 
            data_pn_salvo = instance.data_pn_salvo, 
            pn_salvo = instance.pn_salvo, 
            uf = instance.uf, 
            login_usuario = instance.login_usuario, 
            email_usuario = instance.email_usuario, 
            data_hora_atualizado_status = instance.data_hora_atualizado_status, 
        )