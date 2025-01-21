import os
from models.plano import Plano

class Proyecto:
    def __init__(self, nombre, path):
        self.nombre = nombre
        self.path = path
        self.iniciales = self.obtener_iniciales(nombre)
        self.plano_seleccionado = None  # Inicialmente sin plano seleccionado

    def __repr__(self):
        return f"Proyecto(nombre={self.nombre}, path={self.path})"

    def obtener_iniciales(self, nombre):
        """Obtiene las iniciales de las dos primeras palabras del nombre."""
        palabras = nombre.split("_")
        if len(palabras) >= 2:
            return palabras[0][0] + palabras[1][0]
        return nombre[:2]  # Si hay menos de dos palabras, usa los primeros dos caracteres

    def listar_planos(self):
        """Lista los planos del proyecto, agregando 'Assets' primero y luego los planos en orden numérico."""
        planos = []
        if os.path.exists(self.path) and os.path.isdir(self.path):
            subcarpetas = [
                carpeta for carpeta in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, carpeta)) and carpeta.startswith(self.iniciales)
            ]
            # Ordenar los planos numéricamente (si contienen números)
            subcarpetas.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else float('inf'))
            planos.append("Assets")
            planos.extend(subcarpetas)
        return planos

    def seleccionar_plano(self, nombre_plano):
        """Selecciona un plano basado en el nombre."""
        if nombre_plano == "Assets":
            path_plano = os.path.join(self.path, "_Assets")
            render_path = os.path.join(path_plano, "renders")
            self.plano_seleccionado = Plano(nombre_plano, path_plano, "", render_path, "Comp")
        else:
            path_plano = os.path.join(self.path, nombre_plano)
            render_path = os.path.join(path_plano, "renders")
            self.plano_seleccionado = Plano(nombre_plano, path_plano, nombre_plano.split("_")[-1], render_path, "3D")

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "path": self.path,
            "iniciales": self.iniciales,
            "plano_seleccionado": self.plano_seleccionado.to_dict() if self.plano_seleccionado else None
        }