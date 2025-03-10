from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

def index(request):
    return render(request, 'index.html')

def calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana, periodo_trabalhado):
    # Converter strings de horário para objetos datetime
    formato_hora = "%H:%M"
    inicio_jornada = datetime.strptime(inicio_jornada, formato_hora)
    inicio_refeicao = datetime.strptime(inicio_refeicao, formato_hora)
    fim_refeicao = datetime.strptime(fim_refeicao, formato_hora)
    periodo_trabalho_opcao = periodo_trabalhado
    
    # Cálculo da carga horária semanal total com minutos de compensação incluídos
    carga_horaria_total_semana = hora_semana + (minutos_compensacao or 0)  # Total semanal incluindo compensação
    carga_horaria_diaria = carga_horaria_total_semana / dias_semana  # Carga diária ajustada

    # Calcular intervalo de refeição
    intervalo_refeicao = fim_refeicao - inicio_refeicao
    
    # Lista para armazenar as horas trabalhadas e intervalo de refeição
    horarios_trabalhados = []

    hora_atual = inicio_jornada
    horas_trabalhadas = timedelta(hours=0)

     # Ajustar o valor de "hours" com base em "periodo_trabalho_opcao"
    if periodo_trabalho_opcao == "none":
        hours = 1
    elif periodo_trabalho_opcao in ["clt", "sumula"]:
        hours = 1.1428571
    else:
        raise ValueError("Opção de cálculo inválida. Escolha 'none', 'clt' ou 'sumula'.")

    # Somar horas trabalhadas até o intervalo de refeição
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria and hora_atual < inicio_refeicao:
        hora_entrada = hora_atual
        hora_saida = hora_atual + timedelta(hours=hours)
        
        # Verificar se a próxima hora coincide com o intervalo de refeição
        if hora_saida >= inicio_refeicao:
            horarios_trabalhados.append((hora_entrada.strftime(formato_hora), inicio_refeicao.strftime(formato_hora), "1,00"))
            horas_trabalhadas += timedelta(hours=hours)
            break
        
        horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_saida
        horas_trabalhadas += timedelta(hours=hours)
    
    # Adicionar o intervalo de refeição
    horarios_trabalhados.append((inicio_refeicao.strftime(formato_hora), fim_refeicao.strftime(formato_hora), "0,00"))
    hora_atual = fim_refeicao

    # Continuar somando o restante das horas até atingir a carga horária diária ajustada
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria:
        hora_entrada = hora_atual
        hora_saida = hora_atual + timedelta(hours=hours)
        
        # Verificar se ainda falta menos de uma hora
        if (horas_trabalhadas.total_seconds() / 3600 + 1) > carga_horaria_diaria:
            minutos_restantes = carga_horaria_diaria - horas_trabalhadas.total_seconds() / 3600
            hora_saida = hora_entrada + timedelta(minutes=minutos_restantes * 60)
            horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), f"{minutos_restantes:.2f}"))
            horas_trabalhadas += timedelta(minutes=minutos_restantes * 60)
            break
        
        horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_saida
        horas_trabalhadas += timedelta(hours=hours)

    # Calcular diferença de carga horária após as subtrações
    diferenca_carga_horaria = carga_horaria_diaria - horas_trabalhadas.total_seconds() / 3600
    
    # Retornar a carga horária total semanal, carga horária diária ajustada, horas trabalhadas e a diferença
    return carga_horaria_total_semana, carga_horaria_diaria, horas_trabalhadas.total_seconds() / 3600, diferenca_carga_horaria, horarios_trabalhados

def calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana, periodo_trabalhado):
    # Converter strings de horário para objetos datetime
    formato_hora = "%H:%M"
    fim_jornada = datetime.strptime(fim_jornada, formato_hora)
    inicio_refeicao = datetime.strptime(inicio_refeicao, formato_hora)
    fim_refeicao = datetime.strptime(fim_refeicao, formato_hora)
    periodo_trabalho_opcao = periodo_trabalhado
    
    # Cálculo da carga horária diária e total
    carga_horaria_diaria = hora_semana / dias_semana
    carga_horaria_total = carga_horaria_diaria + (minutos_compensacao / dias_semana) if minutos_compensacao else carga_horaria_diaria

    # Calcular intervalo de refeição
    intervalo_refeicao = fim_refeicao - inicio_refeicao

    # Lista para armazenar os períodos trabalhados
    horarios_trabalhados = []

    # Começar pelo fim da jornada
    hora_atual = fim_jornada
    horas_trabalhadas = timedelta(hours=0)

    # Ajustar o valor de "hours" com base em "periodo_trabalho_opcao"
    if periodo_trabalho_opcao == "none":
        hours = 1
    elif periodo_trabalho_opcao in ["clt", "sumula"]:
        hours = 1.1428571
    else:
        raise ValueError("Opção de cálculo inválida. Escolha 'none', 'clt' ou 'sumula'.")

    # Subtrair horas trabalhadas após o intervalo de refeição
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria and hora_atual > fim_refeicao:
        hora_saida = hora_atual
        hora_entrada = hora_atual - timedelta(hours=hours)
        
        # Verificar se a próxima hora coincide com o fim do intervalo de refeição
        if hora_entrada <= fim_refeicao:
            horarios_trabalhados.append((fim_refeicao.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
            horas_trabalhadas += timedelta(hours=hours)
            break
        
        horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_entrada
        horas_trabalhadas += timedelta(hours=hours)

    # Adicionar o intervalo de refeição
    horarios_trabalhados.append((inicio_refeicao.strftime(formato_hora), fim_refeicao.strftime(formato_hora), "0,00"))
    hora_atual = inicio_refeicao

    # Continuar subtraindo o restante das horas até atingir a carga horária total ajustada
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_total:
        hora_saida = hora_atual
        hora_entrada = hora_atual - timedelta(hours=hours)
        
        # Verificar se ainda falta menos de uma hora
        if (horas_trabalhadas.total_seconds() / 3600 + 1) > carga_horaria_total:
            minutos_restantes = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600
            hora_entrada = hora_saida - timedelta(minutes=minutos_restantes * 60)
            horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), f"{minutos_restantes:.2f}"))
            horas_trabalhadas += timedelta(minutes=minutos_restantes * 60)
            break
        
        horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        hora_atual = hora_entrada
        horas_trabalhadas += timedelta(hours=hours)

    # Ordenar os períodos trabalhados pelo horário de entrada
    horarios_trabalhados.sort(key=lambda periodo: datetime.strptime(periodo[0], formato_hora))

    # Calcular o horário de início da jornada
    inicio_jornada = hora_atual.strftime(formato_hora)

    # Calcular a diferença de carga horária após as subtrações
    diferenca_carga_horaria = carga_horaria_total - horas_trabalhadas.total_seconds() / 3600

    return carga_horaria_total, minutos_compensacao, horas_trabalhadas.total_seconds() / 3600, diferenca_carga_horaria, horarios_trabalhados

def calculo_noturno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana):
    #hora trabalhada equivale a 1,1428571
    pass

def calculo_noturno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana):
    #hora trabalhada equivale a 1,1428571
    pass

def calculo_escala_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, carga_horaria, periodo_trabalhado):
    # Converter strings de horário para objetos datetime
    formato_hora = "%H:%M"
    inicio_jornada = datetime.strptime(inicio_jornada, formato_hora)
    inicio_refeicao = datetime.strptime(inicio_refeicao, formato_hora)
    fim_refeicao = datetime.strptime(fim_refeicao, formato_hora)
    periodo_trabalho_opcao = periodo_trabalhado
    
    # Converter minutos_compensacao para float (tratar caso seja None ou string vazia)
    minutos_compensacao = float(minutos_compensacao) if minutos_compensacao else 0.0

    # Ajustar a carga horária diária com os minutos de compensação
    carga_horaria_diaria = carga_horaria + (minutos_compensacao / 60)

    # Calcular intervalo de refeição
    intervalo_refeicao = fim_refeicao - inicio_refeicao
    
    # Lista para armazenar as horas trabalhadas e intervalo de refeição
    horarios_trabalhados = []

    hora_atual = inicio_jornada
    horas_trabalhadas = timedelta(hours=0)

    # Ajustar o valor de "hours" com base em "periodo_trabalho_opcao"
    if periodo_trabalho_opcao == "none":
        hours = 1
    elif periodo_trabalho_opcao in ["clt"]: #das 22:00 as 05:00
        hours = 0.85714229
    elif periodo_trabalho_opcao in ["sumula"]:#das 22:00 até o final do expediente trabalhado
        hours = 0.85714229
    else:
        raise ValueError("Opção de cálculo inválida. Escolha 'none', 'clt' ou 'sumula'.")

    # Somar horas trabalhadas até o intervalo de refeição
    while horas_trabalhadas.total_seconds() / 3600 < carga_horaria_diaria:
        # Verificar se o horário atual está dentro do intervalo de refeição
        if inicio_refeicao <= hora_atual < fim_refeicao:
            # Adicionar o intervalo de refeição
            horarios_trabalhados.append((inicio_refeicao.strftime(formato_hora), fim_refeicao.strftime(formato_hora), "0,00"))
            hora_atual = fim_refeicao
            continue  # Pular o intervalo de refeição

        # Calcular o próximo horário de saída
        hora_entrada = hora_atual
        hora_saida = hora_atual + timedelta(hours=hours)

        # Verificar se a próxima hora ultrapassa o intervalo de refeição
        if hora_saida > inicio_refeicao and hora_entrada < inicio_refeicao:
            # Ajustar o horário de saída para o início do intervalo de refeição
            hora_saida = inicio_refeicao

        # Adicionar o período trabalhado
        horarios_trabalhados.append((hora_entrada.strftime(formato_hora), hora_saida.strftime(formato_hora), "1,00"))
        horas_trabalhadas += timedelta(hours=hours)
        hora_atual = hora_saida

        # Verificar se atingiu a carga horária diária
        if horas_trabalhadas.total_seconds() / 3600 >= carga_horaria_diaria:
            break

    # Calcular diferença de carga horária após as subtrações
    diferenca_carga_horaria = carga_horaria_diaria - horas_trabalhadas.total_seconds() / 3600
    
    # Retornar os valores no formato esperado
    return carga_horaria_diaria, carga_horaria_diaria, horas_trabalhadas.total_seconds() / 3600, diferenca_carga_horaria, horarios_trabalhados

def calculo_escala_regressivo():
    #return JsonResponse({"success": False, "modal_id": "periodoTrabalhadoModal"})
    pass

def calcular_adicional_noturno(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f'dados recebidos: {data}')

            def converter_para_float(valor):
                try:
                    return float(valor) if valor else 0.0  # Retorna 0.0 se o valor for None ou string vazia
                except ValueError:
                    return 0.0 

            tipo_calculo = data.get('tipo_calculo')
            periodo_trabalhado = data.get('periodo_trabalhado') or 'none'
            dias_semana = int(data.get('dias_semana', 0))
            hora_semana = converter_para_float(data.get('hora_semana'))
            inicio_jornada = data.get('inicio_jornada') or None
            fim_jornada = data.get('fim_jornada') or None
            inicio_refeicao = data.get('inicio_refeicao')
            fim_refeicao = data.get('fim_refeicao')
            minutos_compensacao = converter_para_float(data.get('minutos_compensacao'))
            carga_horaria = converter_para_float(data.get('carga_horaria'))

            resultado = (0, 0, 0, [])

            
            if tipo_calculo == 'tradicional':
                if inicio_jornada and not fim_jornada:
                    resultado = calculo_diurno_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana, periodo_trabalhado)
                elif fim_jornada and not inicio_jornada:
                    resultado = calculo_diurno_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, hora_semana, dias_semana, periodo_trabalhado)
            else:
                if inicio_jornada and not fim_jornada:
                    resultado = calculo_escala_progressivo(inicio_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, carga_horaria, periodo_trabalhado)
                elif fim_jornada and not inicio_jornada:
                    resultado = calculo_escala_regressivo(fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao, carga_horaria, periodo_trabalhado)

            carga_horaria_total, minutos_compensacao, horas_trabalhadas, diferenca_carga_horaria, horarios_trabalhados = resultado

            def ajustar_carga_horaria(carga_horaria):
                # Verificar se a carga horária é um número inteiro ou float
                if isinstance(carga_horaria, float):
                    # Separar a parte inteira e a parte decimal
                    parte_inteira = int(carga_horaria)
                    parte_decimal = carga_horaria - parte_inteira
                    
                    # Multiplicar a parte decimal por 0.60 e ajustar
                    parte_decimal_ajustada = round(parte_decimal * 0.60, 2)
                    
                    # Concatenar a parte inteira com a parte decimal ajustada
                    carga_horaria_ajustada = parte_inteira + parte_decimal_ajustada
                    return carga_horaria_ajustada
                else:
                    # Se for um número inteiro, retorna o valor original
                    return carga_horaria

            horas = int(hora_semana)  # Parte inteira
            minutos = int((hora_semana - horas) * 60)  # Parte decimal convertida para minutos
            horas_formatadas = f"{horas}h{minutos:02d}"  # Formato 'XhYY'

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
            for entrada, saida, hora_trabalhada in horarios_trabalhados:
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
            horas_trabalhadas = ajustar_carga_horaria(horas_trabalhadas)
            horas_trabalhadas = f"{horas_trabalhadas:.2f}".replace(".", "h")

            diferenca_carga_horaria = ajustar_carga_horaria(diferenca_carga_horaria)
            diferenca_carga_horaria = f"{diferenca_carga_horaria:.2f}".replace(".", "h")

            carga_horaria_total = ajustar_carga_horaria(carga_horaria_total)
            carga_horaria_total = f"{carga_horaria_total:.2f}".replace(".", "h")

            resultado_html = f"""
            <div class="container">
                <p>Horas Trabalhadas:<strong> {horas_trabalhadas} </strong> horas</p>
                <p>Diferença de Carga Horária:<strong> {diferenca_carga_horaria} </strong> horas</p>
                <p>Carga Horária Total:<strong> {carga_horaria_total} </strong></p>
                {tabela_html}
            </div>
            """

            return JsonResponse({"success": True, "resultado_html": resultado_html})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método inválido"})