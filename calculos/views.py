from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

def index(request):
    return render(request, 'index.html')

def calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana):
    # Converter strings de horário para objetos datetime
    formato_hora = "%H:%M"
    inicio_jornada = datetime.strptime(inicio_jornada, formato_hora)
    inicio_refeicao = datetime.strptime(inicio_refeicao, formato_hora)
    fim_refeicao = datetime.strptime(fim_refeicao, formato_hora)
    
    # Cálculo da carga horária diária e armazena o valor original da carga horária
    carga_horaria_diaria = hora_semana / dias_semana
    carga_horaria_total = carga_horaria_diaria

    # Calcular intervalo de refeição
    intervalo_refeicao = fim_refeicao - inicio_refeicao
    
    # Lista para armazenar as horas trabalhadas e intervalo de refeição
    periodos_trabalhados = []

    hora_atual = inicio_jornada
    horas_trabalhadas = timedelta(hours=0)

    # Somar horas trabalhadas até o intervalo de refeição
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria and hora_atual < inicio_refeicao:
        hora_entrada = hora_atual
        hora_saida = hora_atual + timedelta(hours=1)
        
        # Verificar se a próxima hora coincide com o intervalo de refeição
        if hora_saida >= inicio_refeicao:
            periodos_trabalhados.append((hora_entrada.strftime(formato_hora), inicio_refeicao.strftime(formato_hora), "1,00"))
            horas_trabalhadas += timedelta(hours=1)
            break
        
        periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_saida
        horas_trabalhadas += timedelta(hours=1)
    
    # Adicionar o intervalo de refeição
    periodos_trabalhados.append((inicio_refeicao.strftime(formato_hora), fim_refeicao.strftime(formato_hora), "0,00"))
    hora_atual = fim_refeicao

    # Continuar somando o restante das horas até atingir a carga horária diária
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_total:
        hora_entrada = hora_atual
        hora_saida = hora_atual + timedelta(hours=1)
        
        # Verificar se ainda falta menos de uma hora
        if (horas_trabalhadas.total_seconds() / 3600 + 1) > carga_horaria_total:
            minutos_restantes = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600
            hora_saida = hora_entrada + timedelta(minutes=minutos_restantes * 60)
            periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), f"{minutos_restantes:.2f}"))
            horas_trabalhadas += timedelta(minutes=minutos_restantes * 60)
            break
        
        periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_saida
        horas_trabalhadas += timedelta(hours=1)

    # Calcular diferença de carga horária após as subtrações
    diferenca_carga_horaria = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600

    # Retornar a carga horária total, horas trabalhadas e a diferença da carga horária e os períodos
    return carga_horaria_total, horas_trabalhadas.total_seconds() / 3600, diferenca_carga_horaria, periodos_trabalhados

def calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana):
    # Converter strings de horário para objetos datetime
    formato_hora = "%H:%M"
    fim_jornada = datetime.strptime(fim_jornada, formato_hora)
    inicio_refeicao = datetime.strptime(inicio_refeicao, formato_hora)
    fim_refeicao = datetime.strptime(fim_refeicao, formato_hora)
    
    # Cálculo da carga horária diária e armazena o valor original da carga horária
    carga_horaria_diaria = hora_semana / dias_semana
    carga_horaria_total = carga_horaria_diaria

    # Calcular intervalo de refeição
    intervalo_refeicao = fim_refeicao - inicio_refeicao

    # Lista para armazenar os períodos trabalhados
    periodos_trabalhados = []

    # Começar pelo fim da jornada
    hora_atual = fim_jornada
    horas_trabalhadas = timedelta(hours=0)

    # Subtrair horas trabalhadas após o intervalo de refeição
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria and hora_atual > fim_refeicao:
        hora_saida = hora_atual
        hora_entrada = hora_atual - timedelta(hours=1)
        
        # Verificar se a próxima hora coincide com o fim do intervalo de refeição
        if hora_entrada <= fim_refeicao:
            periodos_trabalhados.append((fim_refeicao.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
            horas_trabalhadas += timedelta(hours=1)
            break
        
        periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_entrada
        horas_trabalhadas += timedelta(hours=1)

    # Adicionar o intervalo de refeição
    periodos_trabalhados.append((inicio_refeicao.strftime(formato_hora), fim_refeicao.strftime(formato_hora), "0,00"))
    hora_atual = inicio_refeicao

    # Continuar subtraindo o restante das horas até atingir a carga horária diária
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_total:
        hora_saida = hora_atual
        hora_entrada = hora_atual - timedelta(hours=1)
        
        # Verificar se ainda falta menos de uma hora
        if (horas_trabalhadas.total_seconds() / 3600 + 1) > carga_horaria_total:
            minutos_restantes = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600
            hora_entrada = hora_saida - timedelta(minutes=minutos_restantes * 60)
            periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), f"{minutos_restantes:.2f}"))
            horas_trabalhadas += timedelta(minutes=minutos_restantes * 60)
            break
        
        periodos_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_entrada
        horas_trabalhadas += timedelta(hours=1)

    # Ordenar os períodos trabalhados pelo horário de entrada (hora_entrada)
    periodos_trabalhados.sort(key=lambda periodo: datetime.strptime(periodo[0], formato_hora))

    # Calcular o horário de início da jornada
    inicio_jornada = hora_atual.strftime(formato_hora)

    # Calcular a diferença de carga horária após as subtrações
    diferenca_carga_horaria = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600

    return carga_horaria_total, horas_trabalhadas.total_seconds() / 3600, diferenca_carga_horaria, periodos_trabalhados

def calculo_noturno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao):
    #hora trabalhada equivale a 1,1428571
    pass

def calculo_noturno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao):
    #hora trabalhada equivale a 1,1428571
    pass

def calculo_escala_progressivo():
    #return JsonResponse({"success": False, "modal_id": "tipoCalculoModal"})
    pass

def calculo_escala_regressivo():
    #return JsonResponse({"success": False, "modal_id": "tipoCalculoModal"})
    pass

def calcular_adicional_noturno(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f'dados recebidos: {data}')

            def converter_para_float(valor):
                try:
                    return float(valor) if valor else None
                except ValueError:
                    return None

            tipo_calculo = data.get('tipo_calculo')
            dias_semana = int(data.get('dias_semana'))
            hora_semana = converter_para_float(data.get('hora_semana'))
            inicio_jornada = data.get('inicio_jornada') or None
            fim_jornada = data.get('fim_jornada') or None
            inicio_refeicao = data.get('inicio_refeicao')
            fim_refeicao = data.get('fim_refeicao')
            minutos_compensacao = converter_para_float(data.get('minutos_compensacao')) or None
            carga_horaria = converter_para_float(data.get('carga_horaria'))

            if carga_horaria is None:
                carga_horaria = 0

            resultado = (0, 0, 0, [])
            
            if tipo_calculo == 'tradicional':
                if inicio_jornada and not fim_jornada:
                    resultado = calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana)
                elif fim_jornada and not inicio_jornada:
                    resultado = calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana)
            else:
                if inicio_jornada and not fim_jornada:
                    resultado = calculo_escala_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana)
                elif fim_jornada and not inicio_jornada:
                    resultado = calculo_escala_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana)

            carga_horaria_total, horas_trabalhadas, diferenca_carga_horaria, periodos_trabalhados = resultado

            tabela_html = """
            <table class="table table-striped table-bordered">
                <thead class="thead-dark">
                    <tr>
                        <th>Entrada</th>
                        <th>Saída</th>
                        <th>Horas Trabalhadas</th>
                    </tr>
                </thead>
                <tbody>
            """
            for entrada, saida, hora_trabalhada in periodos_trabalhados:
                tabela_html += f"""
                            <tr>
                                <td>{entrada}</td>
                                <td>{saida}</td>
                                <td>{hora_trabalhada}</td>
                            </tr>
                            """
            tabela_html += """
                            </tbody>
                        </table>
                        """

            resultado_html = f"""
                        <div class="container">
                            <div class="row">
                                <div class="col-md-12">
                                    <p><strong>Dias da Semana:</strong> {dias_semana}</p>
                                    <p><strong>Horas Semanais:</strong> {hora_semana}</p>
                                    <p><strong>Carga Horária Diária:</strong> {carga_horaria_total}</p>
                                    <p><strong>Horas Trabalhadas:</strong> {horas_trabalhadas}</p>
                                    <p><strong>Diferença de Carga Horária:</strong> {diferenca_carga_horaria}</p>
                                    {tabela_html}
                                </div>
                            </div>
                        </div>
                        """

            return JsonResponse({"success": True, "resultado_html": resultado_html})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método inválido"})