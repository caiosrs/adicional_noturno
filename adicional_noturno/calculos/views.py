from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return render(request, 'calculos/index.html')

def calcular_adicional_noturno(request):
    if request.method == 'POST':
        # Obtenção dos valores do formulário
        tipo_calculo = request.POST.get('tipo_calculo', 'tradicional')  # Tradicional como padrão
        dias_semana = float(request.POST.get('dias_semana', 0))
        hora_semana = float(request.POST.get('hora_semana', 0))
        inicio_jornada = request.POST.get('inicio_jornada', '0:00').replace(":", ".")
        fim_jornada = request.POST.get('fim_jornada', '0:00').replace(":", ".")
        inicio_refeicao = request.POST.get('inicio_refeicao', '0:00').replace(":", ".")
        fim_refeicao = request.POST.get('fim_refeicao', '0:00').replace(":", ".")
        minutos_compensacao = float(request.POST.get('minutos_compensacao', 0))

        # Verificação do tipo de cálculo
        if tipo_calculo == 'escala':
            carga_horaria_escala = float(request.POST.get('carga_horaria', 0))
        else:
            carga_horaria_escala = None  # Não usar na opção tradicional

        carga_horaria_tradicional = hora_semana / dias_semana if dias_semana != 0 else 0
        total_carga_horaria = float(inicio_jornada) + carga_horaria_tradicional

        # Preparação dos dados para retornar como JSON
        context = {
            'dias_semana': dias_semana,
            'hora_semana': hora_semana,
            'inicio_jornada': inicio_jornada,
            'fim_jornada': fim_jornada,
            'minutos_compensacao': minutos_compensacao,
            'carga_horaria_tradicional': carga_horaria_tradicional,
            'carga_horaria': carga_horaria_escala,
            'total_carga_horaria': total_carga_horaria
        }

        return JsonResponse(context)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
