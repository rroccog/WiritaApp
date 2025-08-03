# -*- coding: utf-8 -*-
"""
Created on Sat Aug  2 01:05:23 2025

@author: Rocco
"""
from datetime import date
import streamlit as st
import calendar
from datetime import datetime
from datetime import timedelta
import math

# Configuración inicial
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

yy = datetime.today().year

dias_frances = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche"
}

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

valor_minuto = valor_hora/60

duracion_clase = st.sidebar.number_input(
    "Duración de la clase (minutos):", 
    value= 60
)

with st.sidebar:
    st.image("AtelierFrance.png", caption="Constanza Sobarzo L.")

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

col1a, col2a, col3a, col4a, col5a = st.columns(5)
with col1a:
    lunes = st.time_input("Horario lunes", value = None, step=60)
with col2a:
    martes = st.time_input("Horario martes", value = None)
with col3a:
    miercoles = st.time_input("Horario miercoles", value = None)
with col4a:
    jueves = st.time_input("Horario jueves", value = None)
with col5a:
    viernes = st.time_input("Horario viernes", value = None)

# Mostrar selección actual combinada
seleccionados_ordenados = sorted(st.session_state.seleccionados)
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Días de clases:", len(seleccionados_ordenados))
with col2:
    if st.button("Deseleccionar todos los días"):
        st.session_state.seleccionados = set()

n_dias = len(seleccionados_ordenados)
valor_total_aprox = math.ceil(int(n_dias*valor_minuto*duracion_clase) / 1000) * 1000
st.write(f"Son {n_dias} días de clases, lo que hace un valor total de ${str(valor_total_aprox)}")

st.subheader("Resumen")
estudiante = st.text_input("Nombre:")

# Obtenemos el número del mes y el calendario del mes
mes = list(calendar.month_name).index(meses_es_en[mes_esp])
calendario_mes = calendar.monthcalendar(yy, mes)

# Días seleccionados ordenados
dias_seleccionados = sorted(st.session_state.seleccionados)

# Creamos agrupación por semana
semanas_agrupadas = []

for semana in calendario_mes:
    dias_semana = []
    for i, dia in enumerate(semana):
        if dia in dias_seleccionados:
            nombre_dia = date(yy, mes, dia).strftime("%A")
            dias_semana.append(f"{dia} ({nombre_dia})")
    if dias_semana:
        semanas_agrupadas.append(dias_semana)

lun_ini, lun_fin, mar_ini, mar_fin, mie_ini, mie_fin, jue_ini, jue_fin, vie_ini, vie_fin = [],[],[],[],[],[],[],[],[],[]

horarios = {}

if lunes is not None:
    lun_ini = datetime.combine(date.today(), lunes)
    lun_fin = (lun_ini + timedelta(minutes=duracion_clase)).time()
    horarios["Lundi"] = (lunes, lun_fin)

if martes is not None:
    mar_ini = datetime.combine(date.today(), martes)
    mar_fin = (mar_ini + timedelta(minutes=duracion_clase)).time()
    horarios["Mardi"] = (martes, mar_fin)

if miercoles is not None:
    mie_ini = datetime.combine(date.today(), miercoles)
    mie_fin = (mie_ini + timedelta(minutes=duracion_clase)).time()
    horarios["Mercredi"] = (miercoles, mie_fin)

if jueves is not None:
    jue_ini = datetime.combine(date.today(), jueves)
    jue_fin = (jue_ini + timedelta(minutes=duracion_clase)).time()
    horarios["Jeudi"] = (jueves, jue_fin)

if viernes is not None:
    vie_ini = datetime.combine(date.today(), viernes)
    vie_fin = (vie_ini + timedelta(minutes=duracion_clase)).time()
    horarios["Vendredi"] = (viernes, vie_fin)


# Construir el texto de las semanas agrupadas
# Agrupación por semana como tuplas
semanas_agrupadas = []

for semana in calendario_mes:
    dias_semana = []
    for dia in semana:
        if dia in dias_seleccionados and dia != 0:
            nombre_dia_en = date(yy, mes, dia).strftime("%A")  # día en inglés
            nombre_dia_fr = dias_frances.get(nombre_dia_en, nombre_dia_en)
            dias_semana.append((str(dia), nombre_dia_fr))
    if dias_semana:
        semanas_agrupadas.append(dias_semana)

# Construir texto final
lineas = []
for i, semana in enumerate(semanas_agrupadas, start=1):
    partes = []
    for dia, nombre in semana:
        if nombre in horarios:
            ini, fin = horarios[nombre]
            partes.append(f"{nombre} {dia} de {ini.strftime('%H:%M').replace(":", "H")} à {fin.strftime('%H:%M').replace(":", "H")}")
        else:
            partes.append(f"{nombre} {dia}")
    lineas.append(f"• {' - '.join(partes)}")

texto_semanas = "\n".join(lineas)


# Luego lo insertas en el f-string final
mensaje = f"""
Bonsoir {estudiante},

J'espère que tu vas bien.

Comme convenu, voici les dates des cours d'août :
    
{texto_semanas}

Total : {int(n_dias*(duracion_clase/60))} heures x {valor_hora} CLP = {str(valor_total_aprox)} CLP

J'attends ta confirmation et te souhaite une bonne soirée.

À bientôt,

"""

st.text(mensaje)








