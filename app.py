from flask import Flask, jsonify, render_template, request
import os
import json
from config import DIRECTORIO_BASE
from models.proyecto import Proyecto
from models.plano import Plano

app = Flask(__name__, static_folder="static")

CONFIG_FILE = "config_proyecto.json"

# Instancias globales
proyecto_actual = None

def cargar_proyecto_seleccionado():
    """Carga el proyecto y plano seleccionado desde el JSON y crea instancias."""
    global proyecto_actual

    print(">>> Ejecutando cargar_proyecto_seleccionado()")  # Verificar si la función se llama

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as file:
            json.dump({"nombre": "", "path": "", "plano": {}}, file, indent=4)

    with open(CONFIG_FILE, "r") as file:
        data = json.load(file)
        print(">>> JSON CARGADO:", data)  # Verificar contenido del JSON

        nombre_proyecto = data.get("nombre", "")
        path_proyecto = data.get("path", "")
        plano_data = data.get("plano", {})

        if nombre_proyecto and path_proyecto:
            print(f">>> Creando instancia de Proyecto: {nombre_proyecto}")
            proyecto_actual = Proyecto(nombre_proyecto, path_proyecto)

            if plano_data and isinstance(plano_data, dict):
                nombre_plano = plano_data.get("nombre")  # Extraemos el nombre correcto
                print(f">>> Creando instancia de Plano: {nombre_plano}")
                if nombre_plano:
                    proyecto_actual.set_plano(nombre_plano)

    print(">>> Estado actual del proyecto:", proyecto_actual)  # Ver en la terminal
    return proyecto_actual.to_dict() if proyecto_actual else {"nombre": "", "path": "", "plano": None}

def guardar_proyecto_seleccionado(nombre, plano):
    """Guarda el proyecto y plano seleccionado en JSON y actualiza la instancia."""
    global proyecto_actual

    print(f">>> Guardando proyecto: {nombre}, Plano: {plano}")  # Debug

    proyecto_path = os.path.join(DIRECTORIO_BASE, nombre)
    proyecto_actual = Proyecto(nombre, proyecto_path)
    proyecto_actual.set_plano(plano)

    with open(CONFIG_FILE, "w") as file:
        json.dump(proyecto_actual.to_dict(), file, indent=4)

    print(">>> Nuevo estado de config_proyecto.json guardado")

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

@app.route('/planos/<proyecto>')
def obtener_planos(proyecto):
    """Devuelve la lista de planos en formato correcto para el frontend."""
    path_proyecto = os.path.join(DIRECTORIO_BASE, proyecto)
    planos = [{"nombre": "Assets", "path": os.path.join(path_proyecto, "_Assets")}]  # Incluir Assets primero

    if os.path.exists(path_proyecto) and os.path.isdir(path_proyecto):
        subcarpetas = [
            carpeta for carpeta in os.listdir(path_proyecto)
            if os.path.isdir(os.path.join(path_proyecto, carpeta)) and "_" in carpeta
        ]
        # Filtrar solo los planos numéricos (segunda palabra con números)
        subcarpetas = [
            {"nombre": c, "path": os.path.join(path_proyecto, c)}
            for c in subcarpetas if len(c.split("_")) > 1 and c.split("_")[1].isdigit()
        ]
        subcarpetas.sort(key=lambda x: int(x["nombre"].split("_")[1]))  # Orden numérico
        planos.extend(subcarpetas)

    return jsonify(planos)

@app.route('/debug')
def debug_info():
    """Devuelve la información actual de las instancias de Proyecto y Plano"""
    global proyecto_actual

    if proyecto_actual:
        return jsonify(proyecto_actual.to_dict())
    else:
        return jsonify({"error": "No hay proyecto cargado"})

if __name__ == '__main__':
    cargar_proyecto_seleccionado()  # Cargar proyecto al inicio
    app.run(debug=True)