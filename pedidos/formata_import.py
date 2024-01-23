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
from pedidos.models import (BkoReprovado, Credito, Equipe, FamiliaProduto,
                            MotivoCancelamento,Observacao, Produto, TipoAgenda,
                            TipoOferta, Uf, Cargo, TipoPN)

from django.contrib.auth.models import User

class FormatacaoValidacaoInputManual:

    def __init__(self, df: pd.DataFrame, request) -> None:
        self.request = request
        self.coluna_padrao = [
                                'CARIMBO DATA/HORA',
                                'EQUIPE',
                                'CONSULTOR',
                                'CARGO',
                                'DATA',
                                'ATIVIDADE',
                                'CNPJ',
                                'RAZÃO SOCIAL',
                                'FAMÍLIA DE PRODUTOS',
                                'STATUS',
                                'STATUS PN',
                                'PRODUTO',
                                'QTDE',
                                'VALOR',
                                'MOTIVO CANCELAMENTO',
                                'SIMULAÇÃO',
                                'COTAÇÃO',
                                'PEDIDO',
                                'CRÉDITO',
                                'BKO REPROVADO',
                                'DATA ATIVAÇÃO',
                                'TIPO AGENDA',
                                'DATA AGENDA',
                                'HORA AGENDA',
                                'CAMPANHA',
                                'DATA CAMPANHA',
                                'NOME GESTOR',
                                'CELULAR GESTOR',
                                'E-MAIL GESTOR',
                                'OBSERVAÇÃO 1',
                                'OBSERVAÇÃO 2',
                                'DATA CQV',
                                'BKO CQV',
                                'DATA CRIAÇÃO',
                                'BKO CRIAÇÃO',
                                'DATA ACEITE',
                                'BKO ACEITE',
                                'DATA INPUT',
                                'BKO INPUT',
                                'DATA PN SALVO',
                                'PN SALVO',
                                'ID',
                                'DATA ATUALIZADO',

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
                        'QTDE',
                        'SIMULAÇÃO',
                        'ATIVIDADE',
                        'ID',
                        # 'N° Simulação',
                        # 'N° Pedido',
                        ]

        self.dct_usuarios: dict = self.listar_usuarios()
        self.df = df
        # alterando os titulos para upper
        self.df.columns = self.df.columns.str.upper()

    def validacao_df(self):
        """função responsavel por aplicar as validações dentro do dataframe"""
        progresso = 10

        # verifcação de colunas
        try:
            coluna_tabela = self.df.columns.to_list()
            valida = set(self.coluna_padrao) - set(coluna_tabela)
            if valida:
                error = f'Colunas Não localizadas\n {"|".join(map(str,valida))}'
                SessionManager.salvar_dados(self.request, error, "Erro", progresso)
                return self.df, error
            
        except Exception as e:
            erro = 'Erro nas definições de Colunas! Verifique e tente novamente.'
            SessionManager.salvar_dados(self.request, erro, "Erro", progresso)
            return self.df, erro
        
        SessionManager.salvar_dados(self.request, "Colunas Existentes:: Iniciando Verificação colunas", "Concluído", progresso)

        # verificação de colunas de datas
        try:
            for coluna in self.colunas_data:
                coluna_data = self.df[coluna]
                status, desc_status = self.valida_se_data(coluna_data)
                if not desc_status in 'OK':
                    SessionManager.salvar_dados(self.request, desc_status, "Erro", progresso)
                    return self.df, desc_status

        except Exception as e:
            erro = 'Erro na conversão de colunas de datas! Verifique o padrão e tente novamente.'
            SessionManager.salvar_dados(self.request, erro, "Erro",progresso)
            return self.df, erro
        
        progresso = progresso + 15
        SessionManager.salvar_dados(self.request, "Colunas Datas:: Iniciando Verificação colunas com Datas", "Concluído", progresso)

        # verificação de colunas de numeros
        try:
            for coluna in self.colunas_int:
                coluna_int = self.df[coluna]
                status, desc_status = self.valida_se_inteiro(coluna_int)
                if not desc_status in 'OK':
                    SessionManager.salvar_dados(self.request, f'Erro na conversão de colunas de numeros inteiros! Verifique o padrão e tente novamente. {coluna}', "Erro",progresso)
                    return self.df, desc_status

        except Exception as e:
            erro = f'Erro na conversão de colunas de numeros inteiros! Verifique o padrão e tente novamente. {coluna}'
            SessionManager.salvar_dados(self.request, erro, "Erro",progresso)
            return self.df,  erro
        
        progresso = progresso + 40
        SessionManager.salvar_dados(self.request, "Colunas Inteiros:: Iniciando Verificação colunas de numeros", "Concluído", progresso)

        # =======================================================================================================
        # verificação de chaves
        # =======================================================================================================
        try:
            self.df['STATUS PN'] = self.df['STATUS PN'].apply(self.valida_chave_pn)
            self.df['EQUIPE'] = self.df['EQUIPE'].apply(self.valida_chave_equipe)
            self.df['FAMÍLIA DE PRODUTOS'] = self.df['FAMÍLIA DE PRODUTOS'].apply(self.valida_chave_familia_produto)
            self.df['MOTIVO CANCELAMENTO'] = self.df['MOTIVO CANCELAMENTO'].apply(self.valida_chave_motivo_cancelamento)
            self.df['TIPO AGENDA'] = self.df['TIPO AGENDA'].apply(self.valida_chave_agenda)
            self.df['PRODUTO'] = self.df['PRODUTO'].apply(self.valida_chave_produto)
            self.df['CAMPANHA'] = self.df['CAMPANHA'].apply(self.valida_chave_tipo_oferta)
            self.df['CARGO'] = self.df['CARGO'].apply(self.valida_chave_cargo)
            self.df['STATUS'] = self.df['STATUS'].apply(self.valida_chave_status)
            self.df['CRÉDITO'] = self.df['CRÉDITO'].apply(self.valida_chave_credito)
            self.df['BKO REPROVADO'] = self.df['BKO REPROVADO'].apply(self.valida_chave_bko_reprovado)
            self.df['CELULAR GESTOR'] = self.df['CELULAR GESTOR'].apply(self.formatar_numero_telefone)
            self.df['OBSERVAÇÃO 1'] = self.df['OBSERVAÇÃO 1'].apply(self.valida_chave_observacao)
            self.df['OBSERVAÇÃO 2'] = self.df['OBSERVAÇÃO 2'].apply(self.valida_chave_observacao)

            progresso = progresso + 17
            SessionManager.salvar_dados(self.request, "Colunas Dados:: Iniciando Verificação colunas informações Complementares", "Concluído", progresso)

            # convertendo as colunas para data
            try:
                for col in self.colunas_data:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            except Exception as e:
                SessionManager.salvar_dados(self.request, f'Erro ao tentar converter a coluna "{col}".', "Erro", progresso)
                return self.df, f'Erro ao tentar converter a coluna "{col}".'
            
            progresso = progresso + 10
            SessionManager.salvar_dados(self.request, "Colunas Inteiros:: Iniciando Verificação colunas informações Complementares", "Concluído", progresso)

            return self.df, "OK"

        except Exception as e:
                SessionManager.salvar_dados(self.request, f'Erro ao nomear chaves estrangeiras.{e}', "Erro", progresso)
                return self.df, f'Erro ao nomear chaves estrangeiras.{e}'

    ########################################################################################################################
    # AÇÕES ORM DJANGO
    ########################################################################################################################

    ########################################################################################################################
    # verificação de numero de telefone
    ########################################################################################################################
    def formatar_numero_telefone(self, numero):
        # Verifica se o número tem a quantidade correta de dígitos
        try:
            num_digto = ''.join(filter(str.isdigit, str(numero)))

            if len(num_digto) == 0:
                return numero
            elif len(num_digto) < 13:
                return numero
            
            # Formata o número de acordo com o padrão desejado
            numero_formatado = f"+{num_digto[:2]} ({num_digto[2:4]}) {num_digto[4:9]}-{num_digto[9:]}"
            
            return numero_formatado
        except Exception as e:
            raise Exception(e)
    ########################################################################################################################
    # listar usuarios
    ########################################################################################################################
    def listar_usuarios(self):
        """retorna os usuarios do User"""
        try:
            usuarios= User.objects.all().values('first_name', 'last_name', 'id')
            listagem = {}

            for usuario in usuarios:
                nome = f"{usuario['first_name']} {usuario['last_name']}".upper()
                listagem[nome] = usuario['id']

            return listagem
        except Exception as e:
            raise Exception(e)

    ########################################################################################################################
    # verificação de datas e numeros inteiros
    ########################################################################################################################
    def valida_se_data(self, col_data: pd.Series):
        try:
            col_filtrada = col_data.dropna()
            nome_col = col_data.name
            for index, value in col_filtrada.items():
                try:

                    pd.to_datetime(value)
                    
                except ValueError:
                    return False, f"Formato de data invalido! coluna: {nome_col} index:{index + 2}  valor: {value}"

            return True, 'OK'   
        except Exception as e:
             raise Exception(e)
        
    def valida_se_inteiro(self, col_data: pd.Series):
        try:
            col_filtrada = col_data.dropna()
            nome_col = col_data.name
            for index, value in col_filtrada.items():
                try:
                    int(value)
                except ValueError:
                    return False, f"Formato de numero invalido! coluna: {nome_col} index:{index + 2}  valor: {value}"

            return True, 'OK'  
        except Exception as e:
            raise Exception(e)      
    ########################################################################################################################
    # validação de chaves
    ########################################################################################################################
    def valida_chave_status(self, status_loc: str):
        try:
            resultado = DescricaoStatus.objects.filter(descricao_Status = status_loc.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 4
        except Exception as e:
            return 4
        
    def valida_chave_observacao(self, obs: str):
        try:
            resultado = Observacao.objects.filter(observacao = obs.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_agenda(self, agenda: str):
        try:
            resultado = TipoAgenda.objects.filter(tipo_agenda = agenda.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_motivo_cancelamento(self, motivo: str):
        try:
            resultado = MotivoCancelamento.objects.filter(motivo_cancelamento = motivo.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_bko_reprovado(self, bko_repr: str):
        try:
            resultado = BkoReprovado.objects.filter(bko_reprovado = bko_repr.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_credito(self, credt: str):
        try:
            resultado = Credito.objects.filter(credito = credt.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1

    def valida_chave_produto(self, produto_loc: str):
        try:
            resultado = Produto.objects.filter(produto = produto_loc.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_consultor(self, consultor_nome: str):
        try:
            nome_id = self.dct_usuarios.get(consultor_nome.upper())
            if nome_id:
                return nome_id
            else:
                return 1
        except Exception as e:
            return 1
        
    def valida_chave_equipe(self, equipe_loc: str):
        try:
            resultado = Equipe.objects.filter(equipe = equipe_loc.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 5
        except Exception as e:
            return 5
        
    def valida_chave_tipo_oferta(self, tipo_oferta: str):
        try:
            resultado = TipoOferta.objects.filter(oferta = tipo_oferta.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 1
        except Exception as e:
            return 1

    def valida_chave_uf(self, uf_loc: str):
        try:
            resultado = Uf.objects.filter(uf = uf_loc.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 3  
        except Exception as e:
            return 3
        
    def valida_chave_familia_produto(self, familia_produto_loc: str):
        try:
            resultado = FamiliaProduto.objects.filter(familia_produto = familia_produto_loc.upper()).first() 

            if resultado:

                # print(resultado)
                return resultado.id
            else:
                return 5 
        except Exception as e:
            return 5
        
    def valida_chave_cargo(self, cargo: str):
        try:
            resultado = Cargo.objects.filter(cargo = cargo.upper()).first() 

            if resultado:
                # print(resultado)
                return resultado.id
            else:
                return 5
        except Exception as e:
            return 5
            
    def valida_chave_pn(self, pn: str):
        try:
            resultado = TipoPN.objects.filter(tipo_PN = pn.upper()).first() 

            if resultado:
                return resultado.id
            else:
                return 12
        except Exception as e:
            return 12