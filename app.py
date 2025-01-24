from flask import Flask, jsonify, render_template, request
import os
import json
import platform
import subprocess
from tkinter import Tk, filedialog
from config import DIRECTORIO_BASE
from models.proyecto import Proyecto
from models.plano import Plano
from models.programa import Programa

app = Flask(__name__, static_folder="static")

# Archivos de configuración
CONFIG_FILE = "config_proyecto.json"  # Proyectos y planos
CONFIG_PROGRAMS = "config.json"  # Rutas de programas

# Instancia Global del Proyecto Actual
proyecto_actual = None
programas_instanciados = []  # Lista global para almacenar instancias de programas


# ==================== PROYECTOS Y PLANOS ====================

def cargar_proyecto_seleccionado():
    """Carga el proyecto y plano seleccionado desde el JSON y crea instancias."""
    global proyecto_actual

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as file:
            json.dump({"nombre": "", "path": "", "plano": {}}, file, indent=4)

    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)

        nombre_proyecto = data.get("nombre", "")
        path_proyecto = data.get("path", "")
        plano_data = data.get("plano", {})

        if nombre_proyecto and path_proyecto:
            proyecto_actual = Proyecto(nombre_proyecto, path_proyecto)
            if plano_data and isinstance(plano_data, dict):
                nombre_plano = plano_data.get("nombre")
                if nombre_plano:
                    proyecto_actual.set_plano(nombre_plano)

    return proyecto_actual.to_dict() if proyecto_actual else {"nombre": "", "path": "", "plano": None}

def guardar_proyecto_seleccionado(nombre, plano):
    """Guarda el proyecto y plano seleccionado en JSON y actualiza la instancia."""
    global proyecto_actual

    proyecto_path = os.path.join(DIRECTORIO_BASE, nombre)
    proyecto_actual = Proyecto(nombre, proyecto_path)
    proyecto_actual.set_plano(plano)

    with open(CONFIG_FILE, "w") as file:
        json.dump(proyecto_actual.to_dict(), file, indent=4)



def obtener_directorio_base():
    """Obtiene la ruta del directorio base desde config.json."""
    if os.path.exists(CONFIG_PROGRAMS):
        with open(CONFIG_PROGRAMS, "r") as file:
            try:
                data = json.load(file)
                return data.get("proyecto", "")  # Retorna la ruta del proyecto si está configurada
            except json.JSONDecodeError:
                print(">>> Error: config.json corrupto, usando ruta vacía.")
    return ""

@app.route('/proyectos')
def obtener_proyectos():
    """Devuelve la lista de proyectos con `_Assets`, usando la ruta de configuración."""
    directorio_base = obtener_directorio_base()
    proyectos = []

    if os.path.exists(directorio_base) and os.path.isdir(directorio_base):
        for carpeta in sorted(os.listdir(directorio_base)):
            ruta_proyecto = os.path.join(directorio_base, carpeta)
            if os.path.isdir(ruta_proyecto) and os.path.isdir(os.path.join(ruta_proyecto, "_Assets")):
                proyectos.append({"nombre": carpeta, "path": ruta_proyecto})

    # Si no hay proyectos, devolver la opción por defecto
    if not proyectos:
        proyectos.append({"nombre": "Seleccione un proyecto...", "path": ""})

    return jsonify(proyectos)

@app.route('/planos/<proyecto>')
def obtener_planos(proyecto):
    """Devuelve la lista de planos en formato correcto para el frontend."""
    directorio_base = obtener_directorio_base()
    path_proyecto = os.path.join(directorio_base, proyecto)

    # Si la ruta del proyecto no existe o no tiene subcarpetas, mostrar solo "Seleccione un proyecto..."
    if not os.path.exists(path_proyecto) or not os.path.isdir(path_proyecto):
        return jsonify([{"nombre": "Seleccione un proyecto...", "path": ""}])

    planos = [{"nombre": "Assets", "path": os.path.join(path_proyecto, "_Assets")}]  # Incluir Assets primero

    subcarpetas = [
        carpeta for carpeta in os.listdir(path_proyecto)
        if os.path.isdir(os.path.join(path_proyecto, carpeta)) and "_" in carpeta
    ]

    # Filtrar solo los planos numéricos (segunda palabra con números)
    planos_numericos = []
    for carpeta in subcarpetas:
        partes = carpeta.split("_")
        if len(partes) > 1 and partes[1].isdigit():
            planos_numericos.append({
                "nombre": partes[1],  # Mostrar solo el número
                "path": os.path.join(path_proyecto, carpeta)
            })

    # Ordenar por número
    planos_numericos.sort(key=lambda x: int(x["nombre"]))

    # Si no hay planos numéricos, solo mostrar "Seleccione un proyecto..."
    if not planos_numericos:
        return jsonify([{"nombre": "Seleccione un proyecto...", "path": ""}])

    # Agregar los planos ordenados
    planos.extend(planos_numericos)

    return jsonify(planos)

@app.route('/proyecto_seleccionado', methods=["GET", "POST"])
def gestionar_proyecto_seleccionado():
    """Devuelve o guarda el proyecto y el plano seleccionado"""
    if request.method == "POST":
        data = request.json
        if "nombre" in data and "plano" in data:
            guardar_proyecto_seleccionado(data["nombre"], data["plano"])
            return jsonify({"status": "success"})
        return jsonify({"status": "error"}), 400

    return jsonify(cargar_proyecto_seleccionado())

# ==================== CONFIGURACIÓN DE RUTAS ====================

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/config')
def configuracion():
    """Renderiza la página de configuración"""
    return render_template("config.html")

def convertir_ruta_macos(ruta):
    """Convierte rutas de macOS de formato AppleScript a Unix."""
    return ruta.replace(":", "/").replace("Macintosh HD", "")

def seleccionar_ruta(tipo):
    """Abre un diálogo de selección de carpeta (proyecto) o archivo (programas) en el hilo principal."""
    ruta = ""

    if platform.system() == "Darwin":  # macOS
        if tipo == "proyecto":
            ruta = subprocess.run(["osascript", "-e", "choose folder"], capture_output=True, text=True).stdout.strip()
        else:
            ruta = subprocess.run(["osascript", "-e", "choose file"], capture_output=True, text=True).stdout.strip()

        if ruta.startswith("alias "):  # Convertir formato AppleScript a Unix
            ruta = convertir_ruta_macos(ruta.replace("alias ", ""))

    else:  # Windows
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        if tipo == "proyecto":
            ruta = filedialog.askdirectory(title="Seleccionar carpeta de proyectos")
        else:
            ruta = filedialog.askopenfilename(title=f"Seleccionar archivo para {tipo}")

    return ruta

@app.route("/seleccionar-ruta", methods=["POST"])
def seleccionar_ruta_api():
    """API para seleccionar una ruta"""
    data = request.json
    tipo = data.get("tipo")
    ruta = seleccionar_ruta(tipo)
    return jsonify({"ruta": ruta})

@app.route("/guardar-configuracion", methods=["POST"])
def guardar_configuracion():
    """Guarda la configuración en config.json y crea instancias de programas"""
    global programas_instanciados
    data = request.json

    print(">>> Guardando configuración en config.json:", data)  # Debug

    try:
        # Guardar en config.json primero
        with open(CONFIG_PROGRAMS, "w") as file:
            json.dump(data, file, indent=4)
        
        print(">>> Configuración guardada correctamente en config.json")

        # Crear instancias de Programa solo después de guardar correctamente
        programas_instanciados = []
        if "programas" in data:
            for nombre, ruta in data["programas"].items():
                if ruta:  # Solo si tiene una ruta válida
                    programa = Programa(nombre, ruta)
                    programas_instanciados.append(programa)
                    print(f">>> Instanciado: {programa}")

        return jsonify({"status": "success"})
    except Exception as e:
        print(">>> Error guardando configuración:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/cargar-configuracion", methods=["GET"])
def cargar_configuracion():
    """Devuelve la configuración guardada en config.json para el frontend."""
    if os.path.exists(CONFIG_PROGRAMS):
        with open(CONFIG_PROGRAMS, "r") as file:
            try:
                data = json.load(file)
                print(">>> Enviando configuración al frontend:", data)  # Debug
                return jsonify(data)
            except json.JSONDecodeError:
                print(">>> Error: config.json está corrupto. Creando uno nuevo.")
                with open(CONFIG_PROGRAMS, "w") as file:
                    json.dump({"proyecto": "", "programas": {}}, file, indent=4)
    return jsonify({"proyecto": "", "programas": {}})

def cargar_configuracion_guardada():
    """Carga la configuración de programas guardados y los instancia"""
    global programas_instanciados

    if os.path.exists(CONFIG_PROGRAMS):
        with open(CONFIG_PROGRAMS, "r") as file:
            data = json.load(file)
            programas_instanciados = []
            for nombre, ruta in data.get("programas", {}).items():
                if ruta:
                    programa = Programa(nombre, ruta)
                    programas_instanciados.append(programa)
                    print(f">>> Cargado desde JSON: {programa}")



# ==================== PROGRAMAS ====================

def obtener_programas():
    """Carga los programas desde las instancias activas o desde config.json si no hay instancias."""
    global programas_instanciados

    if programas_instanciados:
        return programas_instanciados  # Retorna la lista de objetos directamente

    if not os.path.exists(CONFIG_FILE):
        return []

    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)

    # Convertir los datos del JSON en instancias de `Programa`
    programas_instanciados = [Programa(nombre, ruta) for nombre, ruta in data.get("programas", {}).items()]

    return programas_instanciados

@app.route('/programas')
def obtener_lista_programas():
    """Devuelve la lista de programas configurados."""
    programas = obtener_programas()
    
    # Convertimos los objetos de la clase `Programa` en diccionarios antes de enviarlos
    programas_json = [{"nombre": p.nombre, "ruta": p.ruta} for p in programas]

    print(f"DEBUG - Programas enviados al frontend: {programas_json}")  # Para ver en consola lo que se envía
    return jsonify(programas_json)


@app.route('/abrir-programa', methods=["POST"])
def abrir_programa():
    """Abre el programa seleccionado con el proyecto y plano"""
    data = request.json
    programas = obtener_programas()
    
    # Buscar el programa con el nombre recibido en la solicitud
    programa = next((p for p in programas if p.nombre == data["programa"]), None)

    if programa and os.path.exists(programa.ruta):
        subprocess.Popen([programa.ruta])
        return jsonify({"status": "ok", "programa": programa.nombre})
    else:
        return jsonify({"status": "error", "message": "Programa no encontrado"}), 404




# ==================== DEBUG ====================

@app.route('/debug')
def debug_info():
    """Devuelve la información actual de las instancias de Proyecto y Plano"""
    global proyecto_actual
    return jsonify(proyecto_actual.to_dict()) if proyecto_actual else jsonify({"error": "No hay proyecto cargado"})

@app.route("/debug-programas", methods=["GET"])
def debug_programas():
    """Devuelve todas las instancias de programas activas."""
    global programas_instanciados
    return jsonify([programa.to_dict() for programa in programas_instanciados])

if __name__ == '__main__':
    cargar_proyecto_seleccionado()
    cargar_configuracion_guardada()  # Cargar programas guardados
    programas_instanciados = obtener_programas()  # Cargar programas al inicio
    app.run(debug=True)