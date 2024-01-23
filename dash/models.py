from django.db import models
from django.contrib.auth.models import Group



class UrlDashBoard(models.Model):
    id_url = models.AutoField(primary_key=True)
    nome_dash = models.CharField(max_length=255, blank=True, null=False, verbose_name = 'Titulo')
    url = models.URLField(max_length=2048, null=False, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1)

    
    def __str__(self) -> str:
        return self.nome_dash

    class Meta:
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'

class DescricaoTipo(models.Model):
    id = models.AutoField(primary_key=True)
    descricao_tipo = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return f'{self.descricao_tipo}'
    
    def clean(self):
        pass

class DescricaoStatus(models.Model):
    id = models.AutoField(primary_key=True)
    descricao_status = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return f'{self.descricao_status}'
    
    def clean(self):
        pass

    class Meta:
        verbose_name = 'Descrição Status'
        verbose_name_plural = 'Descrição Status'
        

class DeparaDashBoard(models.Model):
    id_depara = models.AutoField(primary_key=True)
    status = models.ForeignKey(DescricaoStatus, on_delete=models.PROTECT, related_name='status_pk')
    tipo = models.ForeignKey(DescricaoTipo, on_delete=models.PROTECT, related_name='tipo_pk')
    ativo = models.CharField(max_length=3, 
                            blank=False, 
                            default='S',
                            null=True,
                            choices=[
                                ('S', 'Sim'),
                                ('N', 'Não'),
                            ])

    def __str__(self):
        return f'{self.tipo}'