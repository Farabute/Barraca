from flask import Flask, jsonify, render_template, request
import os
import json
from tkinter import Tk, filedialog
from config import DIRECTORIO_BASE
from models.proyecto import Proyecto
from models.plano import Plano
import platform
import subprocess


app = Flask(__name__, static_folder="static")

# Archivos de configuración
CONFIG_FILE = "config_proyecto.json"  # Proyectos y planos
CONFIG_PROGRAMS = "config.json"  # Rutas de programas

# Instancia Global del Proyecto Actual
proyecto_actual = None

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

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/proyectos')
def obtener_proyectos():
    """Devuelve la lista de proyectos con `_Assets`"""
    proyectos = []
    if os.path.exists(DIRECTORIO_BASE) and os.path.isdir(DIRECTORIO_BASE):
        for carpeta in sorted(os.listdir(DIRECTORIO_BASE)):
            ruta_proyecto = os.path.join(DIRECTORIO_BASE, carpeta)
            if os.path.isdir(ruta_proyecto) and os.path.isdir(os.path.join(ruta_proyecto, "_Assets")):
                proyectos.append({"nombre": carpeta, "path": ruta_proyecto})
    return jsonify(proyectos)

@app.route('/planos/<proyecto>')
def obtener_planos(proyecto):
    """Devuelve la lista de planos disponibles en un proyecto"""
    path_proyecto = os.path.join(DIRECTORIO_BASE, proyecto)
    planos = [{"nombre": "Assets", "path": os.path.join(path_proyecto, "_Assets")}]  # Incluir Assets primero

    if os.path.exists(path_proyecto) and os.path.isdir(path_proyecto):
        subcarpetas = [
            carpeta for carpeta in os.listdir(path_proyecto)
            if os.path.isdir(os.path.join(path_proyecto, carpeta)) and "_" in carpeta
        ]
        subcarpetas = [
            {"nombre": c, "path": os.path.join(path_proyecto, c)}
            for c in subcarpetas if len(c.split("_")) > 1 and c.split("_")[1].isdigit()
        ]
        subcarpetas.sort(key=lambda x: int(x["nombre"].split("_")[1]))  # Orden numérico
        planos.extend(subcarpetas)

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
    """Guarda la configuración en config.json"""
    data = request.json
    print(">>> Guardando configuración:", data)  # DEBUG: Ver qué llega desde el frontend

    try:
        with open(CONFIG_PROGRAMS, "w") as file:
            json.dump(data, file, indent=4)
        print(">>> Configuración guardada correctamente")
        return jsonify({"status": "success"})
    except Exception as e:
        print(">>> Error guardando configuración:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/cargar-configuracion", methods=["GET"])
def cargar_configuracion():
    """Carga la configuración de programas desde config.json"""
    if os.path.exists(CONFIG_PROGRAMS):
        with open(CONFIG_PROGRAMS, "r") as file:
            return jsonify(json.load(file))
    return jsonify({})

# ==================== DEBUG ====================

@app.route('/debug')
def debug_info():
    """Devuelve la información actual de las instancias de Proyecto y Plano"""
    global proyecto_actual
    return jsonify(proyecto_actual.to_dict()) if proyecto_actual else jsonify({"error": "No hay proyecto cargado"})

if __name__ == '__main__':
    cargar_proyecto_seleccionado()
    app.run(debug=True)