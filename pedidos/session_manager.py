from datetime import datetime
import time
from django.http import JsonResponse

class SessionManager:
    def obter_progresso(request):
        data = request.session.get('data', {})
        return JsonResponse({'data': data})

    @staticmethod
    def limpar_progresso(request):
        request.session.pop('data', None)
        request.session.save()
        return JsonResponse({'success': True})

    @staticmethod
    def salvar_dados(request, logger, status, progress):
        request.session['data'] = {
            'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'logger': logger,
            'status': status,
            'progress': progress,
        }
        request.session.save()
        time.sleep(1)
        