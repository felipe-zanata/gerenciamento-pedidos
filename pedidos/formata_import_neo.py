import pandas as pd
import os
import django
import ipdb

from pedidos.session_manager import SessionManager

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE','app.settings')

# Configure Django settings
django.setup()
from dash.models import DescricaoStatus
from pedidos.models import Equipe

from django.contrib.auth.models import User

class FormatacaoValidacaoInputManualNeo:

    def __init__(self, df: pd.DataFrame, request=None) -> None:
        self.request = request
        self.coluna_padrao = [
                                'NUMERO',
                                'CPF-CNPJ',
                                'ETAPA',
                                'USUARIO',
                                'EQUIPE',
                                # 'VINCULADO',
                                # 'LOGIN',
                                # 'TIPO',
                                # 'NOME CLIENTE',
                                # 'PRAZO',
                                # 'SLA HORAS',
                                # 'TEMPO',
                                # 'ÚLTIMA MOV',
                                # 'TAGS',
                                # 'TAG USUÁRIO',
                                # 'USUÁRIO ADM',
                                # 'ORIGEM',
                                # 'CADASTRO',
                                # 'ATUALIZACAO',
                                # 'RETORNO FUTURO',
                                # 'COMPLEMENTOS',
                                ]
        self.colunas_data = [
            'DATA',
            'DATA ATIVAÇÃO',
            'DATA AGENDA',
            'DATA CAMPANHA',
            'DATA CQV',
            'DATA CRIAÇÃO',
            'DATA ACEITE',
            'DATA INPUT',
            'DATA ACEITE',
            'DATA PN SALVO',
            # 'DATA PORTABILIDADE',
            # 'DATA INSTALAÇÃO',
        ]
        self.colunas_int = [
                        'NUMERO',
                        # 'N° Simulação',
                        # 'N° Pedido',
                        ]

        # self.dct_usuarios: dict = self.listar_usuarios()
        self.df = df
        # alterando os titulos para upper
        self.df.columns = self.df.columns.str.upper()

    def validacao_df(self):
        """função responsavel por aplicar as validações dentro do dataframe"""
        progresso = 20
        # verifcação de colunas
        try:
            coluna_tabela = self.df.columns.to_list()
            valida = set(self.coluna_padrao) - set(coluna_tabela)
            print(valida)
            if valida:
                error = f'Colunas Não localizadas\n {"|".join(map(str,valida))}'
                SessionManager.salvar_dados(self.request, error, "Erro", progresso)
                return self.df, error
        except Exception as e:
            erro = "Erro ao validar as colunas da tabela."
            SessionManager.salvar_dados(self.request, erro, "Erro", progresso)
            return self.df, error
        
        SessionManager.salvar_dados(self.request, "Colunas Existentes:: Iniciando Verificação colunas", "Concluído", progresso)

        # # verificação de colunas de datas
        # try:

        #     for coluna in self.colunas_data:
        #         coluna_data = self.df[coluna]
        #         status, desc_status = self.valida_se_data(coluna_data)
        #         if not desc_status in 'OK':
        #             print(desc_status)
        #             return self.df, desc_status

        # except Exception as e:
        #     raise Exception(e)

        # verificação de colunas de numeros
        try:
            for coluna in self.colunas_int:
                coluna_int = self.df[coluna]
                status, desc_status = self.valida_se_inteiro(coluna_int)
                if not desc_status in 'OK':
                    SessionManager.salvar_dados(self.request, desc_status, "Erro", progresso)
                    return self.df, desc_status
                
            SessionManager.salvar_dados(self.request, "Colunas Existentes:: Iniciando Verificação colunas de numeros", "Concluído", progresso + 20)

        except Exception as e:
            SessionManager.salvar_dados(self.request, "Erro na conversão de colunas de numeros inteiros!", "Erro", progresso)
            return self.df, 'Erro na conversão de colunas de numeros inteiros! Verifique o padrão e tente novamente.'
        
            
        # =======================================================================================================
        # verificação de chaves
        # =======================================================================================================
        try:
            self.df['EQUIPE'] = self.df['EQUIPE'].apply(self.valida_chave_equipe)
            self.df['ETAPA'] = self.df['ETAPA'].apply(self.valida_chave_status)
  

            # # convertendo as colunas para data
            # for col in self.colunas_data:
            #     self.df[col] = pd.to_datetime(self.df[col], errors='coerce')

            # self.df.to_excel('saida_neo.xlsx')
            SessionManager.salvar_dados(self.request, "Colunas Existentes:: Iniciando Verificação colunas complementares", "Concluído", progresso + 58)

            return self.df, "OK"

        except Exception as e:
            SessionManager.salvar_dados(self.request, str(e), "Erro", progresso)
            raise Exception(e)
        

    ########################################################################################################################
    # AÇÕES ORM DJANGO
    ########################################################################################################################

    ########################################################################################################################
    # verificação de numero de telefone
    ########################################################################################################################
    def formatar_numero_telefone(self, numero):
        # Verifica se o número tem a quantidade correta de dígitos
        num_digto = ''.join(filter(str.isdigit, str(numero)))

        if len(num_digto) == 0:
            return numero
        elif len(num_digto) < 13:
            return numero
        
        # Formata o número de acordo com o padrão desejado
        numero_formatado = f"+{num_digto[:2]} ({num_digto[2:4]}) {num_digto[4:9]}-{num_digto[9:]}"
        
        return numero_formatado
    ########################################################################################################################
    # listar usuarios
    ########################################################################################################################
    def listar_usuarios(self):
        """retorna os usuarios do User"""
        usuarios= User.objects.all().values('first_name', 'last_name', 'id')
        listagem = {}

        for usuario in usuarios:
            nome = f"{usuario['first_name']} {usuario['last_name']}".upper()
            listagem[nome] = usuario['id']

        return listagem

    ########################################################################################################################
    # verificação de datas e numeros inteiros
    ########################################################################################################################
    def valida_se_data(self, col_data: pd.Series):
        col_filtrada = col_data.dropna()
        nome_col = col_data.name
        for index, value in col_filtrada.items():
            try:

                pd.to_datetime(value)
                
            except ValueError:
                return False, f"Formato de data invalido! coluna: {nome_col} index:{index + 2}  valo: {value}"

        return True, 'OK'    
        
    def valida_se_inteiro(self, col_data: pd.Series):
        col_filtrada = col_data.dropna()
        nome_col = col_data.name
        for index, value in col_filtrada.items():
            try:
                int(value)
            except ValueError:
                return False, f"Formato de numero invalido! coluna: {nome_col} index:{index + 2}  valor: {value}"

        return True, 'OK'        
    ########################################################################################################################
    # validação de chaves
    ########################################################################################################################
    def valida_chave_status(self, status_loc: str):
        try:
            resultado = DescricaoStatus.objects.filter(descricao_Status = status_loc.upper()).first() 

            if resultado:
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1

    def valida_chave_equipe(self, equipe_loc: str):
        try:
            resultado = Equipe.objects.filter(equipe = equipe_loc.upper()).first() 

            if resultado:
                return resultado.id
            else:
                return 5
        except Exception as e:
            return 5
