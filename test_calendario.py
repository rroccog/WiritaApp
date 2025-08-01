import streamlit as st
import calendar
from datetime import datetime

# Configuración inicial
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

yy = datetime.today().year

meses_es_en = {
    "Enero": "January", 
    "Febrero": "February",
    "Marzo": "March",
    "Abril": "April",
    "Mayo": "May",
    "Junio": "June",
    "Julio": "July",
    "Agosto": "August",
    "Septiembre": "September",
    "Octubre": "October",
    "Noviembre": "November",
    "Diciembre": "December"
}

dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

# Sidebar con selección múltiple de días para resaltar
# Selector de mes en sidebar
mes_esp = st.sidebar.selectbox(
    'Mes',
    list(meses_es_en.keys()),
    index=datetime.today().month,
    help = "Por defecto se selecciona el mes siguiente"
)


dias_sidebar = st.sidebar.multiselect(
    'Días de clases', 
    dias_semana,
    default=[],
    key="resaltar_dias"
)

valor_hora = st.sidebar.number_input(
    "Valor de la clase $", 
    value= 17000
)

duracion_clase = st.sidebar.number_input(
    "Duración de la clase (horas):", 
    value= 1
)

# Convertir mes a inglés para calendar
mes_ingles = meses_es_en[mes_esp]
month_number = list(calendar.month_name).index(mes_ingles)
month_calendar = calendar.monthcalendar(yy, month_number)

# Estado para días seleccionados en calendario
if "seleccionados" not in st.session_state:
    st.session_state.seleccionados = set()

st.subheader(f"{mes_esp} {yy}")

# Mostrar calendario con checkboxes para seleccionar/deseleccionar días
cols = st.columns(7)
for i, d in enumerate(dias_semana):
    cols[i].markdown(f"**{d}**")

for semana in month_calendar:
    cols = st.columns(7)
    for i, dia in enumerate(semana):
        if dia == 0:
            cols[i].markdown(" ")
        else:
            key = f"dia_{dia}"
            marcado = dia in st.session_state.seleccionados or dias_semana[i] in dias_sidebar
            # Checkbox muestra si está marcado desde calendario o sidebar
            nuevo_estado = cols[i].checkbox(label=str(dia), value=marcado, key=key)
            if nuevo_estado:
                st.session_state.seleccionados.add(dia)
            else:
                st.session_state.seleccionados.discard(dia)

# Mostrar selección actual combinada
seleccionados_ordenados = sorted(st.session_state.seleccionados)
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Días de clases:", len(seleccionados_ordenados))
with col2:
    if st.button("Deseleccionar todos los días"):
        st.session_state.seleccionados = set()


st.subheader("Resumen")

n_dias = len(seleccionados_ordenados)
st.write(f"Son {n_dias} días de clases, lo que hace un valor total de ${str(int(n_dias*valor_hora*duracion_clase))}")

st.write(f"Son {n_dias} días de clases, lo que hace un valor total de ${str(int(n_dias*valor_hora*duracion_clase))}")
