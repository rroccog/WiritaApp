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
import requests
import pandas as pd
import streamlit.components.v1 as components

# Configuración inicial
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
tab1, tab2 = st.tabs(["Calcular valores", "Calendario (google drive)"])

icon_texto = "AtelierFrance_texto.png"
icon_icon = "AtelierFrance_Icono.png"
st.logo(icon_texto, icon_image=icon_icon)

yy = datetime.today().year
hora = datetime.today().hour
dd = datetime.today().day

# Función para cargar feriados con caché
@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_feriados():
    try:
        url = 'https://api.boostr.cl/holidays.json'
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        data = response.json()
        
        # Verificar que la respuesta tenga el formato esperado
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            feriados_raw = data['data']
            df = pd.DataFrame(feriados_raw)
            
            # Verificar que el DataFrame tenga la columna 'date'
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df['anio'] = df['date'].dt.year
                df['mes'] = df['date'].dt.month
                df['dia'] = df['date'].dt.day
                return df[['anio', 'mes', 'dia']]
            else:
                st.warning("La API de feriados no devolvió el formato esperado. Continuando sin feriados.")
                return pd.DataFrame(columns=['anio', 'mes', 'dia'])
        else:
            st.warning("La API de feriados devolvió datos vacíos. Continuando sin feriados.")
            return pd.DataFrame(columns=['anio', 'mes', 'dia'])
            
    except requests.exceptions.RequestException as e:
        if "429" in str(e):
            st.info("⏳ API de feriados temporalmente ocupada. Los feriados se cargarán en el próximo intento.")
        else:
            st.warning(f"Error al conectar con la API de feriados: {e}. Continuando sin feriados.")
        return pd.DataFrame(columns=['anio', 'mes', 'dia'])
    except ValueError as e:
        st.warning(f"Error al procesar los datos de feriados: {e}. Continuando sin feriados.")
        return pd.DataFrame(columns=['anio', 'mes', 'dia'])
    except Exception as e:
        st.warning(f"Error inesperado con los feriados: {e}. Continuando sin feriados.")
        return pd.DataFrame(columns=['anio', 'mes', 'dia'])

# Cargar feriados usando el caché
feriados_df = cargar_feriados()

if hora < 17:
    saludo = "Bonjour"
else:
    saludo = "Bonsoir"
    
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

# Selector de mes en sidebar
mes_esp = st.sidebar.selectbox(
    'Mes',
    list(meses_es_en.keys()),
    index=datetime.today().month-1
)

# Sidebar con selección múltiple de días para resaltar
dias_sidebar = st.sidebar.multiselect(
    'Días de clases', 
    dias_semana,
    default=[],
    key="resaltar_dias"
)

valor_hora = st.sidebar.number_input(
    "Valor de la clase $", 
    value= 17000,
    step = 1000
)

valor_minuto = valor_hora/60

duracion_clase = st.sidebar.number_input(
    "Duración de la clase (minutos):", 
    value= 60,
    step = 15
)

with st.sidebar:
    st.image("AtelierFrance.png", caption="Constanza Sobarzo L.")

# Convertir mes a inglés para calendar
mes_ingles = meses_es_en[mes_esp]
month_number = list(calendar.month_name).index(mes_ingles)
month_calendar = calendar.monthcalendar(yy, month_number)

feriados_dias = feriados_df[feriados_df['mes'] == month_number]
dias_feriados = list(feriados_dias['dia'])

# Estado para días seleccionados en calendario
if "seleccionados" not in st.session_state:
    st.session_state.seleccionados = set()

# Estado para rastrear cambios en sidebar
if "dias_sidebar_prev" not in st.session_state:
    st.session_state.dias_sidebar_prev = []

with tab1:
    st.subheader(f"{mes_esp} {yy}")
    
    # Detectar cambios en dias_sidebar y actualizar seleccionados automáticamente
    if dias_sidebar != st.session_state.dias_sidebar_prev:
        # Limpiar seleccionados
        st.session_state.seleccionados = set()
        
        # Agregar días que coincidan con los seleccionados en sidebar
        for semana in month_calendar:
            for i, dia in enumerate(semana):
                if dia != 0 and dias_semana[i] in dias_sidebar:
                    fecha_dia = datetime(yy, month_number, dia)
                    hoy = datetime.today()
                    es_pasado = fecha_dia.date() < hoy.date()
                    es_feriado = dia in dias_feriados
                    
                    # Solo agregar si no es pasado ni feriado
                    if not es_pasado and not es_feriado:
                        st.session_state.seleccionados.add(dia)
        
        st.session_state.dias_sidebar_prev = dias_sidebar
    
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
                es_feriado = dia in dias_feriados
                label = f"{dia} 🎉" if es_feriado else str(dia)
                
                fecha_dia = datetime(yy, month_number, dia)
                hoy = datetime.today()
                es_pasado = fecha_dia.date() < hoy.date()

                # Marcado basado solo en el estado de sesión
                marcado = (not es_pasado) and (dia in st.session_state.seleccionados)

                nuevo_estado = cols[i].checkbox(
                    label=label,
                    value=marcado,
                    key=key,
                    disabled=es_pasado
                )

                # Actualizar estado de sesión basado en la interacción del usuario
                if nuevo_estado and not es_pasado:
                    st.session_state.seleccionados.add(dia)
                elif not nuevo_estado:
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
            st.rerun()

    n_dias = len(seleccionados_ordenados)
    valor_total_aprox = round(int(n_dias*valor_minuto*duracion_clase), -1)
    st.write(f"Son {n_dias} días de clases, lo que hace un valor total de ${str(valor_total_aprox)}")

    st.subheader("Resumen")

    # Obtenemos el número del mes y el calendario del mes
    mes = list(calendar.month_name).index(meses_es_en[mes_esp])
    calendario_mes = calendar.monthcalendar(yy, mes)

    # Días seleccionados ordenados
    dias_seleccionados = sorted(st.session_state.seleccionados)

    # Creamos agrupación por semana
    semanas_agrupadas = []

    for semana in calendario_mes:
        dias_semana_temp = []
        for i, dia in enumerate(semana):
            if dia in dias_seleccionados:
                nombre_dia = date(yy, mes, dia).strftime("%A")
                dias_semana_temp.append(f"{dia} ({nombre_dia})")
        if dias_semana_temp:
            semanas_agrupadas.append(dias_semana_temp)

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

    # Agrupación por semana como tuplas
    semanas_agrupadas = []

    for semana in calendario_mes:
        dias_semana_lista = []
        for dia in semana:
            if dia in dias_seleccionados and dia != 0:
                nombre_dia_en = date(yy, mes, dia).strftime("%A")  # día en inglés
                nombre_dia_fr = dias_frances.get(nombre_dia_en, nombre_dia_en)
                dias_semana_lista.append((str(dia), nombre_dia_fr))
        if dias_semana_lista:
            semanas_agrupadas.append(dias_semana_lista)

    # Construir texto final
    lineas = []
    for i, semana in enumerate(semanas_agrupadas, start=1):
        partes = []
        for dia, nombre in semana:
            if nombre in horarios:
                ini, fin = horarios[nombre]
                partes.append(f"{nombre} {dia} de {ini.strftime('%H:%M').replace(':', 'H')} à {fin.strftime('%H:%M').replace(':', 'H')}")
            else:
                partes.append(f"{nombre} {dia}")
        lineas.append(f"• {' - '.join(partes)}")

    texto_semanas = "\n".join(lineas)

    estudiante = st.text_input("Nombre:") 
       
    mensaje = f"""
{saludo} {estudiante},

J'espère que tu vas bien.

Comme convenu, voici les dates des cours d'août :
            
{texto_semanas}

Total : {(n_dias*(duracion_clase/60))} heures x {valor_hora} CLP = {str(valor_total_aprox)} CLP

J'attends ta confirmation et te souhaite une bonne soirée.

À bientôt,

"""

    st.text(mensaje)


with tab2:
    components.iframe(
        "https://docs.google.com/spreadsheets/d/1TOelWaElp_Yaebzl9TWWxC0N32Hl6ox1L7zBXGU9TnI/edit?gid=0#gid=0",
        height=1200,
        width=1200,
        scrolling=True
    )
