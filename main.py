from flask import Flask, jsonify
import requests
from embalse import Embalse
from geopy.distance import geodesic
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.debug = False

embalses = []

limiter = Limiter(
    get_remote_address,  # Función para obtener la dirección IP del cliente
    # Límite por defecto de 5 solicitudes por minuto
    default_limits=["5 per minute"]
)

limiter.init_app(app)


@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Límite específico para esta ruta
def login():
    return jsonify(message="¡Login exitoso!")


# URLs de las apis que se van a consumir
API_URLAGUA = "https://gd201aca37fcec3-sw4rm.adb.eu-madrid-1.oraclecloudapps.com/ords/swarm/agua/"
API_URLEMBALSE = "https://gd201aca37fcec3-sw4rm.adb.eu-madrid-1.oraclecloudapps.com/ords/swarm/embalse/"
API_URLLIST = "https://gd201aca37fcec3-sw4rm.adb.eu-madrid-1.oraclecloudapps.com/ords/swarm/listado/"

# Bearer Token para la autenticación
BEARER = "eI54Ss9kqP5KwhyoHf9uXg"

# Calcula la distancia entre dos coordenadas


def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers


# Ruta para obtener los datos de un embalse en base a su latitud y longitud


@app.route('/obtener-embalse/<float:lat>/<float:lon>')
def obtener_embalse(lat, lon):
    headers = {
        'Authorization': f'Bearer {BEARER}'
    }
    try:
        # Realiza la petición GET a la API externa con los headers que incluyen el Bearer Token
        response = requests.get(API_URLLIST, headers=headers)

        # Si la petición fue exitosa (código 200)
        if response.status_code == 200:
            # Convierte los datos en formato JSON
            datos = response.json()
            # Crea una lista de objetos Embalse
            for item in datos["items"]:
                print(item)
                embalse = Embalse(
                    alt_cimien=item.get("alt_cimien"),
                    cauce=item.get("cauce"),
                    ccaa=item.get("ccaa"),
                    codigo=item.get("codigo"),
                    cota_coron=item.get("cota_coron"),
                    demarc=item.get("demarc"),
                    embalse=item.get("embalse"),
                    informe=item.get("informe"),
                    links=item.get("links"),
                    nombre=item.get("nombre"),
                    provincia=item.get("provincia"),
                    tipo=item.get("tipo"),
                    x=item.get("x"),
                    y=item.get("y")
                )
                embalses.append(embalse)
            # Coordenadas del cliente
            coord_cliente = (lat, lon)
            # Distancia máxima
            distancia_max = float(10000)
            # Embalse más cercano
            embalses_cercanos = []

            # Recorre la lista de embalses
            for embalse in embalses:
                # Coordenadas del embalse
                coord_embalse = (float(embalse.x.replace(',', '.')),
                                 float(embalse.y.replace(',', '.')))

                # Calcula la distancia entre el cliente y el embalse
                distancia = calculate_distance(coord_cliente, coord_embalse)
                print(distancia, distancia_max)
                # Si la distancia es menor a la distancia máxima y es menor a la distancia mínima
                if distancia < distancia_max:
                    # Actualiza el embalse
                    embalses_cercanos.append(embalse)

            # Envía los datos al cliente en formato JSON
            return jsonify([embalse.__dict__ for embalse in embalses_cercanos])
        else:
            # Si hubo un error en la respuesta, lo devolvemos
            return f"Error en la API. Código de estado: {response.status_code}"

    except Exception as e:
        # En caso de excepción, muestra el error
        return jsonify({"error": str(e)}), 500


def obtener_listado():
    headers = {
        "Authorization": f"Bearer {BEARER}"
    }
    try:
        # Realiza la petición GET a la API externa con los headers que incluyen el Bearer Token
        response = requests.get(API_URLLIST, headers=headers)

        # Si la petición fue exitosa (código 200)
        if response.status_code == 200:
            # Convierte los datos en formato JSON
            datos = response.json()
            # Crea una lista de objetos Embalse
            for item in datos["items"]:
                embalse = Embalse(
                    alt_cimien=item.get("alt_cimien"),
                    cauce=item.get("cauce"),
                    ccaa=item.get("ccaa"),
                    codigo=item.get("codigo"),
                    cota_coron=item.get("cota_coron"),
                    demarc=item.get("demarc"),
                    embalse=item.get("embalse"),
                    informe=item.get("informe"),
                    links=item.get("links"),
                    nombre=item.get("nombre"),
                    provincia=item.get("provincia"),
                    tipo=item.get("tipo"),
                    x=item.get("x"),
                    y=item.get("y")
                )
                embalses.append(embalse)

            for embalse in embalses:
                print(embalse.nombre)

            return embalses  # Envía los datos al cliente en formato JSON
        else:
            # Si hubo un error en la respuesta, lo devolvemos
            return f"Error en la API. Código de estado: {response.status_code}"

    except Exception as e:
        # En caso de excepción, muestra el error
        return jsonify({"error": str(e)}), 500


@ app.route('/')
def home():
    return "Datos SW4RM Embalses"


if __name__ == '__main__':
    # Ejecuta la aplicación Flask en el puerto 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
