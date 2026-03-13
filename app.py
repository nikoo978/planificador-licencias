import streamlit as st
from datetime import datetime, timedelta
import holidays
import calendar
import pandas as pd

# ---------------------------
# CONFIGURACION
# ---------------------------

st.set_page_config(
    page_title="Planificador de Licencias",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Planificador de Licencias")

# ---------------------------
# MESES EN ESPAÑOL
# ---------------------------

meses_es = {
1:"Enero",
2:"Febrero",
3:"Marzo",
4:"Abril",
5:"Mayo",
6:"Junio",
7:"Julio",
8:"Agosto",
9:"Septiembre",
10:"Octubre",
11:"Noviembre",
12:"Diciembre"
}

# ---------------------------
# FERIADOS ARGENTINA
# ---------------------------

feriados_ar = holidays.country_holidays("AR", years=range(2020,2040))

dias_es = [
"Lunes","Martes","Miércoles","Jueves",
"Viernes","Sábado","Domingo"
]

turnos = ["A","B","C","D"]

base_turno = datetime(2026,3,10).date()

# ---------------------------
# FORMATO FECHA
# ---------------------------

def formatear_fecha(fecha):
    return fecha.strftime("%d/%m/%Y")

# ---------------------------
# FUNCION TURNO
# ---------------------------

def obtener_turno(fecha):

    diff = (fecha-base_turno).days

    if diff < 0:
        return ""

    return turnos[diff % 4]

# ---------------------------
# CALCULO PLAZO
# ---------------------------

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

# ---------------------------
# INPUTS
# ---------------------------

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

# ---------------------------
# CALCULO
# ---------------------------

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

    c1,c2,c3 = st.columns(3)

    c1.metric("Último día",formatear_fecha(ultimo))
    c2.metric("Total de días",total)
    c3.metric("Días de guardia",dias_guardia)

# ---------------------------
# TABLA DETALLE
# ---------------------------

    tabla=[]

    f=fecha_inicio

    while f<=ultimo:

        tabla.append({
            "Fecha":formatear_fecha(f),
            "Día":dias_es[f.weekday()],
            "Turno":obtener_turno(f),
            "Feriado":feriados_ar.get(f,"")
        })

        f+=timedelta(days=1)

    df=pd.DataFrame(tabla)

    def colorear_filas(row):

        fecha = datetime.strptime(row["Fecha"], "%d/%m/%Y").date()

        if row["Feriado"] != "":
            return ["background-color:#ff4d4d;color:white"] * len(row)

        if fecha.weekday() >= 5:
            return ["background-color:#fff3b0;color:black"] * len(row)

        return [""] * len(row)

    styled = df.style.apply(colorear_filas, axis=1)

    st.dataframe(styled,use_container_width=True)

# ---------------------------
# GENERAR MESES
# ---------------------------

    meses=[]

    actual=fecha_inicio.replace(day=1)

    while actual<=ultimo:

        meses.append((actual.year,actual.month))

        if actual.month==12:
            actual=actual.replace(year=actual.year+1,month=1)
        else:
            actual=actual.replace(month=actual.month+1)

# ---------------------------
# CSS CALENDARIO
# ---------------------------

    st.markdown("""
<style>

.calendar-container{
display:flex;
gap:40px;
overflow-x:auto;
padding-bottom:10px;
}

.calendar{
background:#2d3142;
padding:20px;
border-radius:8px;
min-width:520px;
}

.month-title{
text-align:center;
color:white;
font-size:20px;
margin-bottom:10px;
}

.grid{
display:grid;
grid-template-columns:repeat(7,70px);
}

.day-name{
text-align:center;
color:#cfd6e6;
padding:5px;
font-size:12px;
}

.day{
height:70px;
border:1px solid #444;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
font-size:16px;
color:white;
}

.licencia{ background:#8bd17c; }
.finde{ background:#f2d04f; color:black;}
.feriado{ background:#f07a7a; }
.inicio{ background:#5aa0e6; }
.fin{ background:#b277e3; }
.fuera{ background:#1e1e2e; }

.turno{
font-size:12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# GENERAR CALENDARIO
# ---------------------------

    html = '<div class="calendar-container">'

    for year,month in meses:

        html += '<div class="calendar">'
        html += f'<div class="month-title">{meses_es[month]} {year}</div>'
        html += '<div class="grid">'

        for d in ["L","M","X","J","V","S","D"]:
            html += f'<div class="day-name">{d}</div>'

        cal = calendar.monthcalendar(year,month)

        for semana in cal:

            for dia in semana:

                if dia==0:

                    html += '<div class="day fuera"></div>'

                else:

                    fecha=datetime(year,month,dia).date()

                    clase="day"

                    en_ciclo = fecha_inicio <= fecha <= ultimo

                    if fecha in feriados_ar:
                        clase+=" feriado"

                    elif en_ciclo:

                        if fecha==fecha_inicio:
                            clase+=" inicio"

                        elif fecha==ultimo:
                            clase+=" fin"

                        elif fecha.weekday()>=5:
                            clase+=" finde"

                        else:
                            clase+=" licencia"

                    else:
                        clase+=" fuera"

                    fecha_str=formatear_fecha(fecha)

                    if fecha in feriados_ar:
                        tooltip=f"{fecha_str} - Feriado: {feriados_ar.get(fecha)}"
                    elif fecha.weekday()>=5:
                        tooltip=f"{fecha_str} - Fin de semana"
                    else:
                        tooltip=f"{fecha_str} - Día hábil | Turno {obtener_turno(fecha)}"

                    turno_text=""

                    if obtener_turno(fecha)==turno:
                        turno_text=f'<div class="turno">{turno}</div>'

                    html += f'<div class="{clase}" title="{tooltip}">{dia}{turno_text}</div>'

        html += "</div></div>"

    html += "</div>"

    st.markdown(html,unsafe_allow_html=True)
