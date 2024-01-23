from django.contrib import admin
from .models import UrlDashBoard, DescricaoStatus, DeparaDashBoard, DescricaoTipo

# Register your models here.


class DeparaDashBoardAdmin(admin.ModelAdmin):
    list_display = ('status', 'tipo', 'ativo')

admin.site.register(UrlDashBoard)
admin.site.register(DescricaoTipo)
admin.site.register(DescricaoStatus)
admin.site.register(DeparaDashBoard, DeparaDashBoardAdmin)
admin.site.index_title = 'Features area'
admin.site.site_header = 'My project'
admin.site.site_title = 'HTML title from adminsitration'