import streamlit as st
from datetime import datetime, timedelta
import holidays
import pandas as pd

# -----------------------
# CONFIGURACION PAGINA
# -----------------------

st.set_page_config(
    page_title="Planificador de Licencias",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Planificador de Licencias")

# -----------------------
# DIAS EN ESPAÑOL
# -----------------------

dias_es = [
    "Lunes","Martes","Miércoles","Jueves",
    "Viernes","Sábado","Domingo"
]

# -----------------------
# FERIADOS ARGENTINA
# -----------------------

feriados_ar = holidays.country_holidays("AR")

# -----------------------
# INPUTS
# -----------------------

col1,col2,col3 = st.columns(3)

with col1:
    fecha_inicio = st.date_input(
        "Fecha de inicio",
        format="DD/MM/YYYY"
    )

with col2:
    dias_habiles = st.number_input(
        "Días hábiles",
        min_value=1,
        value=10
    )

with col3:
    turno = st.selectbox(
        "Turno",
        ["A","B","C","D"]
    )

turnos = ["A","B","C","D"]

base_turno = datetime(2026,3,10).date()

# -----------------------
# FUNCION TURNO
# -----------------------

def obtener_turno(fecha):

    diff = (fecha-base_turno).days

    if diff < 0:
        return ""

    return turnos[diff % 4]

# -----------------------
# CALCULO PLAZO
# -----------------------

def calcular_plazo(fecha_inicio,dias_habiles):

    fecha = fecha_inicio
    contador = 1
    dias = [fecha]

    while contador < dias_habiles:

        fecha += timedelta(days=1)

        if fecha.weekday() >= 5:
            continue

        if fecha in feriados_ar:
            continue

        contador += 1
        dias.append(fecha)

    return dias

# -----------------------
# BOTON
# -----------------------

if st.button("Calcular"):

    dias = calcular_plazo(fecha_inicio,dias_habiles)

    ultimo = max(dias)
    total = (ultimo-fecha_inicio).days + 1

    dias_guardia = 0
    f = fecha_inicio

    while f <= ultimo:

        if obtener_turno(f) == turno:
            dias_guardia += 1

        f += timedelta(days=1)

    # -----------------------
    # RESULTADOS
    # -----------------------

    c1,c2,c3 = st.columns(3)

    c1.metric("Último día", ultimo.strftime("%d/%m/%Y"))
    c2.metric("Total de días", total)
    c3.metric("Días de guardia", dias_guardia)

    # -----------------------
    # TABLA
    # -----------------------

    tabla = []

    f = fecha_inicio

    while f <= ultimo:

        tabla.append({
            "Fecha": f.strftime("%d/%m/%Y"),
            "Día": dias_es[f.weekday()],
            "Turno": obtener_turno(f),
            "Feriado": feriados_ar.get(f,"")
        })

        f += timedelta(days=1)

    df = pd.DataFrame(tabla)

    # -----------------------
    # COLORES CON CONTRASTE
    # -----------------------

    def resaltar_dias(row):

        fecha = datetime.strptime(row["Fecha"],"%d/%m/%Y").date()

        # feriado
        if row["Feriado"] != "":
            return ["background-color:#ff6b6b; color:black"] * len(row)

        # fin de semana
        if fecha.weekday() >= 5:
            return ["background-color:#ffe066; color:black"] * len(row)

        return [""] * len(row)

    styled_df = df.style.apply(resaltar_dias,axis=1)

    # -----------------------
    # MOSTRAR TABLA
    # -----------------------

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=500
    )