from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

def index(request):
    return render(request, 'index.html')

def calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana):
    #hora trabalhada equivale a 1
    pass

def calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao):
    #hora trabalhada equivale a 1
    pass

def calculo_noturno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao):
    #hora trabalhada equivale a 1,1428571
    pass

def calculo_noturno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao):
    #hora trabalhada equivale a 1,1428571
    pass

def calcular_adicional_noturno(request):
    if request.method == 'POST':
        try:
            # Carregar os dados do JSON recebido
            data = json.loads(request.body)
            print(f'dados recebidos: {data}')

            # Função para converter valores para float, tratando strings vazias
            def converter_para_float(valor):
                try:
                    return float(valor) if valor else None
                except ValueError:
                    return None

            # Coletar os dados do formulário
            tipo_calculo = data.get('tipo_calculo')
            dias_semana = int(data.get('dias_semana'))
            hora_semana = converter_para_float(data.get('hora_semana'))
            inicio_jornada = data.get('inicio_jornada') or None
            fim_jornada = data.get('fim_jornada') or None
            inicio_refeicao = data.get('inicio_refeicao')
            fim_refeicao = data.get('fim_refeicao')
            minutos_compensacao = converter_para_float(data.get('minutos_compensacao')) or None
            carga_horaria = converter_para_float(data.get('carga_horaria'))

            # Adicione uma verificação se a carga_horaria é None, caso seja necessário
            if carga_horaria is None:
                # Se a carga horária não for necessária para o cálculo, você pode definir um valor padrão
                carga_horaria = 0  # Ou qualquer valor padrão que faça sentido

            resultado = 0
            
            # Lógica para direcionar para a função de cálculo correta
            if tipo_calculo == 'tradicional':
                if inicio_jornada:
                    inicio_jornada_hora = datetime.strptime(inicio_jornada, "%H:%M").time()
                    if inicio_jornada_hora > datetime.strptime("05:00", "%H:%M").time() and inicio_jornada_hora < datetime.strptime("15:00", "%H:%M").time():
                        resultado = calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana)
                    elif fim_jornada and fim_jornada > datetime.strptime("05:00", "%H:%M").time() and fim_jornada < datetime.strptime("22:00", "%H:%M").time():
                        resultado = calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao)
                    else:
                        return JsonResponse({"success": False, "modal_id": "tipoCalculoModal", "message": "Condições não atendidas para o cálculo."})

            # Prepare o resultado HTML
            resultado_html = f"""
            <p>Dias da Semana: {dias_semana}</p>
            <p>Horas Semanais: {hora_semana}</p>
            <p>Resultados:</p>
            <table>
                <thead>
                    <tr>
                        <th>Entrada</th>
                        <th>Saída</th>
                        <th>Hora Trabalhada</th>
                    </tr>
                </thead>
                <tbody>
                    {resultado}
                </tbody>
            </table>
            """

            return JsonResponse({"success": True, "resultado_html": resultado_html})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método inválido"})
