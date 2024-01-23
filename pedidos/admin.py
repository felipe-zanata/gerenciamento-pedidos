from django.contrib import admin
from . import models

# Register your models here.
# admin.site.register(models.DadosPedidos)
# admin.site.register(models.DadosPedidosDeletados)
admin.site.register(models.TipoOferta)
admin.site.register(models.Cargo)
admin.site.register(models.Equipe)
admin.site.register(models.Uf)
admin.site.register(models.FamiliaProduto)
admin.site.register(models.Produto)
admin.site.register(models.TipoPN)
admin.site.register(models.BkoReprovado)
admin.site.register(models.Credito)
admin.site.register(models.Observacao)
admin.site.register(models.MotivoCancelamento)
admin.site.register(models.TipoAgenda)