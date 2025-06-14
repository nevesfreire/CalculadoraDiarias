
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import math

st.title("Calculadora de Diárias para TRTs")
# Controles principais
st.markdown(
    """
    <div style='background-color:#ffeb3b; padding:10px; border-left:5px solid #ffc107; margin-bottom:20px; color:#000'>
        <strong>Atenção:</strong> essa é uma <strong>ESTIMATIVA</strong> das diárias. 
        O valor exato será calculado durante a sua Solicitação de Diárias no SIGEO.
    </div>
    """,
    unsafe_allow_html=True
)

auxilio_alimentacao_mensal = 1784.42
diaria_ministro_STF = 1545.54
with st.expander("⚙️ Área restrita: alterar valores"):
    senha = st.text_input("Senha:", type="password")

    if senha == "1234":
        st.success("Acesso liberado ✅")

        col3, col4 = st.columns([1, 1])

        with col3:
            diaria_input = st.text_input("Valor da diária do Ministro STF (R$):", value="1545.54")
            try:
                diaria_ministro_STF = float(diaria_input)
            except ValueError:
                diaria_ministro_STF = 1545.54

        with col4:
            auxilio_input = st.text_input("Auxílio alimentação (valor mensal em R$):", value="1784.42")
            try:
                auxilio_alimentacao_mensal = float(auxilio_input)
            except ValueError:
                auxilio_alimentacao_mensal = 1784.42
    elif senha != "":
        st.error("Senha incorreta.")


desconto_dia_util = auxilio_alimentacao_mensal / 22
# Cálculo das diárias baseado no percentual
valores_diarias = {
    'Técnico Judiciário': {'Sede TRT': math.floor(diaria_ministro_STF * 0.45 * 100) / 100,
                           'Outra Localidade': math.floor(diaria_ministro_STF * 0.36 * 100) / 100},
    'Analista Judiciário': {'Sede TRT': math.floor(diaria_ministro_STF * 0.55 * 100) / 100,
                            'Outra Localidade': math.floor(diaria_ministro_STF * 0.44 * 100) / 100},
    'Juiz do Trabalho': {'Sede TRT': math.floor(diaria_ministro_STF * 0.90 * 100) / 100,
                         'Outra Localidade': math.floor(diaria_ministro_STF * 0.72 * 100) / 100},
    'Juiz Auxiliar': {'Sede TRT': math.floor(diaria_ministro_STF * 0.95 * 100) / 100,
                      'Outra Localidade': math.floor(diaria_ministro_STF * 0.76 * 100) / 100},
    'Desembargador': {'Sede TRT': math.floor(diaria_ministro_STF * 0.95 * 100) / 100,
                      'Outra Localidade': math.floor(diaria_ministro_STF * 0.76 * 100) / 100},
}

# Teto da diária pela LDO
teto_diaria = 1106.20


# Valor adicional se sem veículo oficial: 80% da diária de Analista
adicional_analista = math.floor(valores_diarias['Analista Judiciário']['Outra Localidade'] * 0.8 * 100) / 100

# Função para calcular diárias
def calcular_diarias(cargo, destino, data_inicio, data_fim,
                     prestara_assistencia, acompanhamento_integral, magistrado_base, veiculo_oficial):
    dias = (data_fim - data_inicio).days + 1
    resultados = []

    valor_base = valores_diarias[cargo][destino]

    if (prestara_assistencia or acompanhamento_integral) and magistrado_base:
        base_magistrado = valores_diarias[magistrado_base][destino]
        if prestara_assistencia:
            valor_base = math.floor(base_magistrado * 0.8 * 100) / 100
        if acompanhamento_integral:
            valor_base = math.floor(base_magistrado * 0.9 * 100) / 100

    total = 0.0

    dias_semana_pt = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }

    adicional = 0
    if not veiculo_oficial:
        adicional_analista_destino = valores_diarias['Analista Judiciário'][destino]
        adicional = math.floor(adicional_analista_destino * 0.8 * 100) / 100

    for i in range(dias):
        data_atual = data_inicio + timedelta(days=i)
        valor_dia = valor_base

        # 🔸 Aplica desconto de 40% se viagem excede 7 dias
        if dias > 7:
            valor_dia *= 0.6  # 60% do valor original

        if i == dias - 1:
            valor_dia /= 2

        if data_atual.weekday() < 5:
            valor_dia -= desconto_dia_util

        adicional_dia = 0
        if not veiculo_oficial:
            if dias == 1:
                adicional_dia = adicional
            else:
                if i == 0 or i == dias - 1:
                    adicional_dia = adicional / 2

        teto_dia = teto_diaria
        if i == dias - 1:
            teto_dia /= 2

        valor_final = min(valor_dia + adicional_dia, teto_dia)

        resultados.append({
            'Data': data_atual.strftime("%d/%m/%Y"),
            'Dia da Semana': dias_semana_pt[data_atual.weekday()],
            'Valor da Diária (R$)': '%.2f' % round(valor_final, 2)
        })

        total += valor_final

    return resultados, total



# Seletor de cargo
cargo = st.selectbox("Cargo:", list(valores_diarias.keys()))

# ✅ Linha do seletor de destino + link para sedes
col1, col2 = st.columns([2, 1])

with col1:
    destino = st.radio("Destino:", ['Sede TRT', 'Outra Localidade'], horizontal=True)

with col2:
    with st.expander("Quais são as sedes dos TRTs?"):
        st.write("""
        - TRT 1 — Rio de Janeiro (RJ)
        - TRT 2 — São Paulo (SP)
        - TRT 3 — Belo Horizonte (MG)
        - TRT 4 — Porto Alegre (RS)
        - TRT 5 — Salvador (BA)
        - TRT 6 — Recife (PE)
        - TRT 7 — Fortaleza (CE)
        - TRT 8 — Belém (PA)
        - TRT 9 — Curitiba (PR)
        - TRT 10 — Brasília (DF)
        - TRT 11 — Manaus (AM)
        - TRT 12 — Florianópolis (SC)
        - TRT 13 — João Pessoa (PB)
        - TRT 14 — Porto Velho (RO)
        - TRT 15 — Campinas (SP)
        - TRT 16 — São Luís (MA)
        - TRT 17 — Vitória (ES)
        - TRT 18 — Goiânia (GO)
        - TRT 19 — Maceió (AL)
        - TRT 20 — Aracaju (SE)
        - TRT 21 — Natal (RN)
        - TRT 22 — Teresina (PI)
        - TRT 23 — Cuiabá (MT)
        - TRT 24 — Campo Grande (MS)
        """)

col5, col6 = st.columns([1, 1])

with col5:
    data_inicio = st.date_input("Data de Início do Deslocamento:", format="DD/MM/YYYY")

with col6:
    data_fim = st.date_input("Data de Fim do Deslocamento:", format="DD/MM/YYYY")

modalidade_transporte = st.radio(
    "Modalidade de Deslocamento:",
    ["Veículo Oficial", "Aéreo", "Barco/Lancha", "Veículo Próprio", "Ônibus",],
    horizontal=True
)

veiculo_oficial = (modalidade_transporte == "Veículo Oficial")

prestara_assistencia = False
acompanhamento_integral = False
magistrado_base = None

# Controles condicionais aparecem na hora
if cargo in ['Técnico Judiciário', 'Analista Judiciário']:
    prestara_assistencia = st.checkbox("Prestar Assistência Direta a Magistrado?")
    acompanhamento_integral = st.checkbox("Acompanhamento Integral de Magistrado?")

    if prestara_assistencia or acompanhamento_integral:
        magistrado_base = st.selectbox("Escolha o Magistrado de Referência:", ['Juiz do Trabalho', 'Desembargador'])

# Botão de calcular
if st.button("Calcular"):
    if data_fim < data_inicio:
        st.error("Data de fim deve ser posterior ou igual à data de início.")
    else:
        tabela, total = calcular_diarias(
            cargo, destino, data_inicio, data_fim,
            prestara_assistencia, acompanhamento_integral, magistrado_base, veiculo_oficial
        )

        st.subheader("Resumo das Diárias")
        df_resultado = pd.DataFrame(tabela)
        df_resultado.index = df_resultado.index + 1
        st.table(df_resultado)
        st.success(f"**Total de diárias: R$ {total:.2f}**")