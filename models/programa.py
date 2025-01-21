from models.departamento import Departamento

class Programa:
    DEPARTAMENTOS = {
        "After Effects": Departamento.COMP,
        "Nuke": Departamento.COMP,
        "3D Max": Departamento.THREE_D,
        "Maya": Departamento.THREE_D,
        "Cinema4D": Departamento.THREE_D,
        "Houdini": Departamento.THREE_D,
        "Boujou": Departamento.TRACK,
        "PF Track": Departamento.TRACK,
        "3D Equalizer": Departamento.TRACK,
        "Photoshop": Departamento.ART,
        "Illustrator": Departamento.ART,
        "Substance": Departamento.THREE_D
    }

    def __init__(self, nombre, ruta):
        self.nombre = nombre
        self.ruta = ruta
        self.departamento = self.DEPARTAMENTOS.get(nombre, Departamento.ART)  # Default a ART

    def __repr__(self):
        return f"Programa(nombre={self.nombre}, ruta={self.ruta}, departamento={self.departamento})"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "ruta": self.ruta,
            "departamento": self.departamento.value
        }