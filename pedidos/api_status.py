# script para atualizar_pedidos.py
from datetime import datetime, timedelta
from .models import DadosPedidos
from django.utils import timezone
import requests
import os

class AtualizarStatus:
    def obter_token_estrutura_usuario(self):
        token_estrutura: str = os.getenv("TOKEN_ESTRUTURA")
        token_usuario: str = os.getenv("TOKEN_USUARIO")
        painel_id: str = os.getenv("PAINEL_ID")
        return token_estrutura, token_usuario, painel_id

    def obter_horario_consulta_atual(self):
        agora = datetime.now()
        inicio = (agora - timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M:%S")
        fim = agora.strftime("%Y-%m-%d %H:%M:%S")
        return inicio, fim

    def atualizar_pedidos(self):
        url = "https://app.neosales.com.br/producao-painel-integration-v2"
        token_estrutura, token_usuario, painel_id = self.obter_token_estrutura_usuario()
        inicio, fim = self.obter_horario_consulta_atual()
        payload = {
            "tokenEstrutura": token_estrutura,
            "tokenUsuario": token_usuario,
            "dataHoraInicioCarga": inicio,
            "dataHoraFimCarga": fim,
            "painelId": painel_id,
            "outputFormat": "csv",
        }

        headers = {
            'Content-Type': 'text/plain',
            # 'Content-Type': 'application/json',
            'Cookie': '__cflb=02DiuHcRebXBbQZs3gX28EM2MeLsdaT3jC2MMTm36LJzp'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            status= response.text
            print(status)

            for pedido in DadosPedidos.objects.all():
                atividade = pedido.atividade

                if atividade in status:
                    pedido.status = "Novo Status"
                    pedido.data_hora_atualizado_status = timezone.now()
                    pedido.save()

            print("Fim da atualização!")
        except requests.RequestException as e:
            print(f"Erro ao fazer a solicitação à API: {e}")

    # def atualizar_pedidos(self):
    #     # ... (código existente)
    #         # Busque todos os pedidos de uma vez
    #         pedidos = DadosPedidos.objects.all()

    #         # Mapeie os pedidos por atividade para uma busca mais rápida
    #         pedidos_por_atividade = {pedido.atividade: pedido for pedido in pedidos}

    #         # Atualize os pedidos com base no status
    #         with transaction.atomic():
    #             for atividade in pedidos_por_atividade.keys():
    #                 if atividade in status:
    #                     pedido = pedidos_por_atividade[atividade]
    #                     pedido.status = "Novo Status"
    #                     pedido.data_hora_atualizado_status = timezone.now()
    #                     pedido.save()

# if __name__ == "__main__":
#     atualizar_pedidos()
