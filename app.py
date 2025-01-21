from flask import Flask, jsonify, render_template, request
import os
import json
import re
from config import DIRECTORIO_BASE

app = Flask(__name__, static_folder="static")

CONFIG_FILE = "config_proyecto.json"

def cargar_proyecto_seleccionado():
    """Carga el proyecto y plano seleccionado desde el JSON."""
    if not os.path.exists(CONFIG_FILE):  
        with open(CONFIG_FILE, "w") as file:
            json.dump({"nombre": "", "path": "", "plano": "", "plano_path": ""}, file, indent=4)

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def guardar_proyecto_seleccionado(nombre, plano):
    """Guarda el proyecto y plano seleccionado en JSON con sus rutas completas."""
    proyecto_path = os.path.join(DIRECTORIO_BASE, nombre)
    plano_path = os.path.join(proyecto_path, plano) if plano and plano != "Assets" else os.path.join(proyecto_path, "_Assets")

    with open(CONFIG_FILE, "w") as file:
        json.dump({
            "nombre": nombre,
            "path": proyecto_path,
            "plano": plano,
            "plano_path": plano_path
        }, file, indent=4)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/proyectos')
def obtener_proyectos():
    """Devuelve la lista de proyectos (solo los que contienen `_Assets`)."""
    proyectos = []
    if os.path.exists(DIRECTORIO_BASE) and os.path.isdir(DIRECTORIO_BASE):
        for carpeta in sorted(os.listdir(DIRECTORIO_BASE)):
            ruta_proyecto = os.path.join(DIRECTORIO_BASE, carpeta)
            if os.path.isdir(ruta_proyecto) and os.path.isdir(os.path.join(ruta_proyecto, "_Assets")):
                proyectos.append({"nombre": carpeta, "path": ruta_proyecto})
    return jsonify(proyectos)

@app.route('/planos/<proyecto>')
def obtener_planos(proyecto):
    """Devuelve la lista de planos en formato limpio (solo los números) y evita duplicar 'Assets'."""
    path_proyecto = os.path.join(DIRECTORIO_BASE, proyecto)
    planos = []

    if os.path.exists(path_proyecto) and os.path.isdir(path_proyecto):
        subcarpetas = [
            carpeta for carpeta in os.listdir(path_proyecto)
            if os.path.isdir(os.path.join(path_proyecto, carpeta))
        ]
        
        # Asegurar que "Assets" se agregue solo si existe la carpeta "_Assets"
        if "_Assets" in subcarpetas:
            planos.append("Assets")
        
        # Filtrar subcarpetas con números en la segunda palabra
        subcarpetas = [c for c in subcarpetas if len(c.split("_")) > 1 and re.search(r'\d+', c.split("_")[1])]
        subcarpetas.sort(key=lambda x: int(re.search(r'\d+', x.split("_")[1]).group()))  # Orden numérico
        planos.extend(subcarpetas)  # Agregar los planos después de "Assets"

    return jsonify(planos)

@app.route('/proyecto_seleccionado', methods=["GET", "POST"])
def gestionar_proyecto_seleccionado():
    """Devuelve o guarda el proyecto y plano seleccionado en el JSON."""
    if request.method == "POST":
        data = request.json
        if "nombre" in data and "plano" in data:
            guardar_proyecto_seleccionado(data["nombre"], data["plano"])
            return jsonify({"status": "success"})
        return jsonify({"status": "error"}), 400

    return jsonify(cargar_proyecto_seleccionado())

@app.route('/seleccionar_plano', methods=["POST"])
def seleccionar_plano():
    """Guarda el plano seleccionado en JSON con su ruta."""
    data = request.json
    if "plano" in data:
        proyecto_data = cargar_proyecto_seleccionado()
        proyecto_nombre = proyecto_data.get("nombre", "")
        proyecto_path = proyecto_data.get("path", "")

        if proyecto_nombre and proyecto_path:
            plano_nombre = data["plano"]
            plano_path = os.path.join(proyecto_path, plano_nombre) if plano_nombre != "Assets" else os.path.join(proyecto_path, "_Assets")

            # Guardar en JSON
            guardar_proyecto_seleccionado(proyecto_nombre, plano_nombre)

            # Actualizar JSON con la ruta del plano
            with open(CONFIG_FILE, "r+") as file:
                config_data = json.load(file)
                config_data["plano_path"] = plano_path
                file.seek(0)
                json.dump(config_data, file, indent=4)
                file.truncate()

            return jsonify({"status": "success", "plano": plano_nombre, "plano_path": plano_path})

    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(debug=True)