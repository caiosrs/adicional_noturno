// Declarando variáveis globais para armazenar os valores
let diasSemana, horaSemana, inicio_jornada, fim_jornada, inicio_refeicao, fim_refeicao, minutos_compensacao;

document.getElementById('btn-avancar').addEventListener('click', function(event) {
    event.preventDefault();

    // Atribuindo valores às variáveis globais
    diasSemana = document.getElementById('dias_semana') ? document.getElementById('dias_semana').value : null;
    horaSemana = document.getElementById('hora_semana') ? document.getElementById('hora_semana').value : null;
    inicio_jornada = document.getElementById('inicio_jornada') ? document.getElementById('inicio_jornada').value : null;
    fim_jornada = document.getElementById('fim_jornada') ? document.getElementById('fim_jornada').value : null;
    inicio_refeicao = document.getElementById('inicio_refeicao') ? document.getElementById('inicio_refeicao').value : null;
    fim_refeicao = document.getElementById('fim_refeicao') ? document.getElementById('fim_refeicao').value : null;
    minutos_compensacao = document.getElementById('minutos_compensacao') ? document.getElementById('minutos_compensacao').value || 0 : 0;

    // Validações básicas
    if (!diasSemana || diasSemana < 1 || diasSemana > 7) {
        alert('O valor de dias da semana deve ser entre 1 e 7.');
        return;
    }

    if (!horaSemana || horaSemana == 0) {
        alert('A quantidade de horas semanais não pode ser 0.');
        return;
    }

    if (!inicio_jornada && !fim_jornada) {
        alert('Preencha ao menos um dos campos: "Início da Jornada de Trabalho" ou "Término da Jornada de Trabalho".');
        return;
    }

    if (!inicio_refeicao) {
        alert('O campo "Início do Intervalo de Refeição" não pode ser deixado vazio.');
        return;
    }

    if (!fim_refeicao) {
        alert('O campo "Término do Intervalo de Refeição" não pode ser deixado vazio.');
        return;
    }

    // Lógica para determinar se o cálculo é diurno ou noturno
    const inicioJornada = parseInt(inicio_jornada.replace(':', ''));
    const fimJornada = fim_jornada ? parseInt(fim_jornada.replace(':', '')) : null;

    if (inicioJornada > 500 && fimJornada < 2200) {
        // Cálculo diurno
        abrirModalResultados(); // Função para abrir a modal com resultados
    } else if (inicioJornada >= 2159 && fimJornada <= 500) {
        // Cálculo noturno
        abrirModalResultados(); // Função para abrir a modal com resultados
    } else if (inicioJornada >= 2159 && !fim_jornada) {
        // Exibir modal para escolher tipo de cálculo
        const tipoCalculoModal = new bootstrap.Modal(document.getElementById('tipoCalculoModal'));
        tipoCalculoModal.show();
    }
});

function abrirModalResultados() {
    // Função para popular os dados na modal de resultados
    document.getElementById('modal-dias-semana').textContent = diasSemana;
    document.getElementById('modal-hora-semana').textContent = horaSemana;
    document.getElementById('modal-inicio-jornada').textContent = inicio_jornada;
    document.getElementById('modal-fim-jornada').textContent = fim_jornada;
    document.getElementById('modal-minutos-compensacao').textContent = minutos_compensacao;
    document.getElementById('modal-intervalo-refeicao').textContent = `${inicio_refeicao} - ${fim_refeicao}`;

    // Exibir a modal de resultados
    const resultadoModal = new bootstrap.Modal(document.getElementById('resultadoModal'));
    resultadoModal.show();
}

function calcularDiurno() {
    if (!diasSemana || !horaSemana) {
        alert('Os valores de dias da semana e horas semanais são necessários.');
        return;
    }
    
    let carga_horaria_tradicional = horaSemana / diasSemana;
    carga_horaria_tradicional = ajustarCargaHoraria(carga_horaria_tradicional);
    
    console.log('Carga horária ajustada:', carga_horaria_tradicional);
}

// Função para ajustar a carga horária
function ajustarCargaHoraria(carga_horaria_tradicional) {
    let partes = carga_horaria_tradicional.toString().split(',');

    if (partes.length === 1) {
        return carga_horaria_tradicional.toFixed(2).replace('.', ',');
    }

    let parte_inteira = parseInt(partes[0], 10);
    let parte_decimal = parseFloat('0.' + partes[1]) * 100;
    let ajuste_horas_trabalhadas = parte_decimal * 0.6;

    let nova_parte_decimal = Math.round(ajuste_horas_trabalhadas).toString().padStart(2, '0');

    return `${parte_inteira},${nova_parte_decimal}`;
}

// Evento do botão "Calcular" na modal
document.getElementById('btn-calcular').addEventListener('click', function() {
    const tipoCalculo = document.querySelector('input[name="tipo_calculo_modal"]:checked').value;

    // Chamar a função de cálculo apropriada
    if (tipoCalculo === 'diurno') {
        calcularDiurno();
    } else if (tipoCalculo === 'noturno') {
        calcularNoturno(opcaoNoturno);
    } else if (tipoCalculo === 'diurno_noturno') {
        calcularDiurnoNoturno();
    }

    // Fechar a modal após o cálculo
    const tipoCalculoModal = bootstrap.Modal.getInstance(document.getElementById('tipoCalculoModal'));
    tipoCalculoModal.hide();
});
