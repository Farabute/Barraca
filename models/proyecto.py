import os
from models.plano import Plano
from models.area import Area

class Proyecto:
    def __init__(self, nombre, path):
        self.nombre = nombre
        self.path = path
        self.plano = None  # Instancia de Plano

    def set_plano(self, nombre_plano):
        """Asigna un plano al proyecto y genera su ruta"""
        plano_path = os.path.join(self.path, nombre_plano) if nombre_plano != "Assets" else os.path.join(self.path, "_Assets")
        render_path = os.path.join(plano_path, "renders")
        area = self.determinar_area(nombre_plano)
        numero = nombre_plano if nombre_plano.isdigit() else ""

        self.plano = Plano(nombre_plano, plano_path, numero, render_path, area)

    def determinar_area(self, nombre_plano):
        """Determina el área del plano basado en su nombre"""
        if "comp" in nombre_plano.lower():
            return Area.COMP
        elif "track" in nombre_plano.lower():
            return Area.TRACK
        elif "3d" in nombre_plano.lower():
            return Area.LOOKDEV
        elif "art" in nombre_plano.lower():
            return Area.LOOKDEV
        return Area.ANIMATION  # Valor por defecto

    def listar_planos(self):
        """Lista los planos del proyecto"""
        planos = ["Assets"]
        if os.path.exists(self.path) and os.path.isdir(self.path):
            subcarpetas = [
                carpeta for carpeta in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, carpeta)) and "_" in carpeta
            ]
            # Filtrar solo los planos numéricos (segunda palabra con números)
            subcarpetas = [c for c in subcarpetas if len(c.split("_")) > 1 and c.split("_")[1].isdigit()]
            subcarpetas.sort(key=lambda x: int(x.split("_")[1]))  # Orden numérico
            planos.extend(subcarpetas)
        return planos

    def to_dict(self):
        """Devuelve la información del proyecto en formato JSON"""
        return {
            "nombre": self.nombre,
            "path": self.path,
            "plano": self.plano.to_dict() if self.plano else None
        }