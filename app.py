from flask import Flask, render_template, jsonify
import requests
import random

app = Flask(__name__)

# ======================================
# CACHE DE PREDICCIONES
# ======================================

predicciones_api = []

# ======================================
# CONFIGURACION API
# ======================================

API_KEY = "1a08644ddamsh059bc95db1a0977p16f034jsn019a36cd0260"

URL_API = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"

# ======================================
# GRUPOS DEL MUNDIAL 2026
# ======================================

grupos = {

    "Grupo A": [
        "Mexico",
        "Corea del Sur",
        "Chequia",
        "Sudafrica"
    ],

    "Grupo B": [
        "Canada",
        "Bosnia",
        "Catar",
        "Suiza"
    ],

    "Grupo C": [
        "Brasil",
        "Marruecos",
        "Haiti",
        "Escocia"
    ],

    "Grupo D": [
        "Estados Unidos",
        "Paraguay",
        "Australia",
        "Turquia"
    ],

    "Grupo E": [
        "Alemania",
        "Curazao",
        "Costa de Marfil",
        "Ecuador"
    ],

    "Grupo F": [
        "Paises Bajos",
        "Japon",
        "Suecia",
        "Tunez"
    ],

    "Grupo G": [
        "Belgica",
        "Egipto",
        "Iran",
        "Nueva Zelanda"
    ],

    "Grupo H": [
        "España",
        "Cabo Verde",
        "Arabia Saudita",
        "Uruguay"
    ],

    "Grupo I": [
        "Francia",
        "Senegal",
        "Irak",
        "Noruega"
    ],

    "Grupo J": [
        "Argentina",
        "Argelia",
        "Austria",
        "Jordania"
    ],

    "Grupo K": [
        "Portugal",
        "RD Congo",
        "Uzbekistan",
        "Colombia"
    ],

    "Grupo L": [
        "Inglaterra",
        "Croacia",
        "Ghana",
        "Panama"
    ]

}

# ======================================
# CARGAR PREDICCIONES API
# ======================================

def cargar_predicciones():

    global predicciones_api

    querystring = {
        "market": "classic",
        "iso_date": "2018-12-01",
        "federation": "UEFA"
    }

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com",
        "x-rapidapi-key": API_KEY
    }

    try:

        respuesta = requests.get(
            URL_API,
            headers=headers,
            params=querystring,
            timeout=10
        )

        datos = respuesta.json()

        if "data" in datos:

            predicciones_api = datos["data"]

            print(
                f"Predicciones cargadas: {len(predicciones_api)}"
            )

        else:

            predicciones_api = []

    except Exception as e:

        print(
            "Error API:",
            e
        )

        predicciones_api = []

# ======================================
# CREAR TABLA
# ======================================

def crear_tabla(equipos):

    tabla = {}

    for equipo in equipos:

        tabla[equipo] = {

            "PJ": 0,
            "PG": 0,
            "PE": 0,
            "PP": 0,

            "GF": 0,
            "GC": 0,
            "DG": 0,

            "PTS": 0

        }

    return tabla

# ======================================
# SIMULAR PARTIDO
# ======================================

def simular_partido():

    global predicciones_api

    if len(predicciones_api) > 0:

        partido = random.choice(
            predicciones_api
        )

        prediccion = partido["prediction"]

    else:

        prediccion = random.choice([
            "1",
            "X",
            "2"
        ])

    if prediccion == "1":

        goles_local = random.randint(
            1,
            4
        )

        goles_visitante = random.randint(
            0,
            goles_local - 1
        )

    elif prediccion == "2":

        goles_visitante = random.randint(
            1,
            4
        )

        goles_local = random.randint(
            0,
            goles_visitante - 1
        )

    else:

        goles_local = random.randint(
            0,
            3
        )

        goles_visitante = goles_local

    return (
        goles_local,
        goles_visitante
    )

# ======================================
# ACTUALIZAR TABLA
# ======================================

def actualizar_tabla(
    tabla,
    local,
    visitante,
    goles_local,
    goles_visitante
):

    tabla[local]["PJ"] += 1
    tabla[visitante]["PJ"] += 1

    tabla[local]["GF"] += goles_local
    tabla[local]["GC"] += goles_visitante

    tabla[visitante]["GF"] += goles_visitante
    tabla[visitante]["GC"] += goles_local

    if goles_local > goles_visitante:

        tabla[local]["PG"] += 1
        tabla[visitante]["PP"] += 1

        tabla[local]["PTS"] += 3

    elif goles_visitante > goles_local:

        tabla[visitante]["PG"] += 1
        tabla[local]["PP"] += 1

        tabla[visitante]["PTS"] += 3

    else:

        tabla[local]["PE"] += 1
        tabla[visitante]["PE"] += 1

        tabla[local]["PTS"] += 1
        tabla[visitante]["PTS"] += 1

    tabla[local]["DG"] = (
        tabla[local]["GF"]
        - tabla[local]["GC"]
    )

    tabla[visitante]["DG"] = (
        tabla[visitante]["GF"]
        - tabla[visitante]["GC"]
    )

# ======================================
# SIMULAR GRUPO
# ======================================

def simular_grupo(nombre, equipos):

    tabla = crear_tabla(equipos)

    partidos = []

    for i in range(len(equipos)):

        for j in range(i + 1, len(equipos)):

            local = equipos[i]
            visitante = equipos[j]

            goles_local, goles_visitante = simular_partido()

            actualizar_tabla(
                tabla,
                local,
                visitante,
                goles_local,
                goles_visitante
            )

            partidos.append({

                "local": local,
                "visitante": visitante,
                "goles_local": goles_local,
                "goles_visitante": goles_visitante

            })

    clasificacion = sorted(

        tabla.items(),

        key=lambda x: (
            x[1]["PTS"],
            x[1]["DG"],
            x[1]["GF"]
        ),

        reverse=True

    )

    return {

        "grupo": nombre,

        "partidos": partidos,

        "tabla": clasificacion,

        "clasificados": [

            clasificacion[0][0],
            clasificacion[1][0]

        ]

    }

# ======================================
# PAGINA PRINCIPAL
# ======================================

@app.route('/')
def inicio():

    return render_template('index.html')

# ======================================
# SIMULAR MUNDIAL
# ======================================

@app.route('/simular')
def simular():

    cargar_predicciones()

    resultados_grupos = []

    clasificados = {}

    for nombre, equipos in grupos.items():

        resultado = simular_grupo(
            nombre,
            equipos
        )

        resultados_grupos.append(
            resultado
        )

        clasificados[nombre] = resultado["clasificados"]

    return jsonify({

        "total_predicciones": len(predicciones_api),

        "grupos": resultados_grupos,

        "clasificados": clasificados

    })
# ======================================
# EJECUTAR APP
# ======================================

if __name__ == '__main__':

    app.run(debug=True)