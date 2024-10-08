document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('adicional-noturno-form');
    const resultadoModal = new bootstrap.Modal(document.getElementById('resultadoModal'));

    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Impedir o envio padrão do formulário

        // Captura os dados do formulário
        const tipoCalculo = document.querySelector('input[name="tipo_calculo"]:checked').value;
        const diasSemana = document.getElementById('dias_semana').value;
        const horaSemana = document.getElementById('hora_semana').value;
        const inicioJornada = document.getElementById('inicio_jornada').value;
        const fimJornada = document.getElementById('fim_jornada').value;
        const inicioRefeicao = document.getElementById('inicio_refeicao').value;
        const fimRefeicao = document.getElementById('fim_refeicao').value;
        const minutosCompensacao = document.getElementById('minutos_compensacao').value;
        const cargaHoraria = document.getElementById('carga_horaria').value || null;  // Valor opcional

        // Verificações de validação
        if (!diasSemana || diasSemana < 1 || diasSemana > 7) {
            alert('O valor de "Dias da Semana" deve ser entre 1 e 7.');
            return;
        }

        if (!horaSemana || horaSemana == 0) {
            alert('o "Total de Horas Semanais" não pode ser 0.');
            return;
        }

        if (!inicioJornada && !fimJornada) {
            alert('Preencha ao menos um dos campos: "Início da Jornada de Trabalho" ou "Término da Jornada de Trabalho".');
            return;
        }

        if (!inicioRefeicao) {
            alert('O campo "Início do Intervalo de Refeição" não pode ser deixado vazio.');
            return;
        }

        if (!fimRefeicao) {
            alert('O campo "Término do Intervalo de Refeição" não pode ser deixado vazio.');
            return;
        }

        // Verificação adicional se "Escala" for selecionado
        if (tipoCalculo === 'escala' && !cargaHoraria) {
            alert('O campo "Carga Horária" não pode ser deixado vazio para o tipo de cálculo "Escala".');
            return;
        }

        const cargaHorariaFloat = cargaHoraria ? cargaHoraria : null;  // Valor opcional
        
        // Dados para envio
        const formData = {
            tipo_calculo: tipoCalculo,
            dias_semana: diasSemana,
            hora_semana: horaSemana,
            inicio_jornada: inicioJornada,
            fim_jornada: fimJornada,
            inicio_refeicao: inicioRefeicao,
            fim_refeicao: fimRefeicao,
            minutos_compensacao: minutosCompensacao,
            carga_horaria: cargaHorariaFloat  // Valor opcional
        };        

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Exibir o resultado no modal
                document.querySelector('.modal-resultados').innerHTML = data.resultado_html;
                resultadoModal.show();  // Mostrar o modal com os resultados
            } else {
                if (data.modal_id) {
                    // Mostrar o modal indicado na resposta
                    const tipoCalculoModal = new bootstrap.Modal(document.getElementById(data.modal_id));
                    tipoCalculoModal.show();
                } else {
                    alert('Erro: ' + data.error);
                }
            }
        })
        .catch(error => {
            console.error('Erro ao enviar a requisição:', error);
            alert('Ocorreu um erro ao processar o cálculo.');
        });        
    });
});
