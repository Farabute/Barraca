import os
from models.area import Area

class Plano:
    def __init__(self, nombre, path, numero, render_path, area):
        self.nombre = nombre
        self.path = path
        self.numero = numero
        self.render_path = render_path
        self.area = Area(area) if isinstance(area, str) else area  # Convierte string a Enum

    def __repr__(self):
        return f"Plano(nombre={self.nombre}, path={self.path}, numero={self.numero}, render_path={self.render_path}, area={self.area})"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "path": self.path,
            "numero": self.numero,
            "render_path": self.render_path,
            "area": self.area.value  # Guardamos solo el valor del Enum
        }