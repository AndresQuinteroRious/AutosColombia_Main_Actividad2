from datetime import date
import app.main
from app.models import Usuario
from app.services.usuario import calcular_cobertura_semanal

usuarios = [
    Usuario(nombre=f"U{i}", documento=f"DOC{i}", telefono="111", fecha_vencimiento=date.today(), rol="EMPLEADO", turno="MAÑANA", horas_semana=42, ausentismo_horas=0)
    for i in range(4)
]

with open("final_check.txt", "w", encoding="utf-8") as fh:
    fh.write(str(app.main.app.title) + "\n")
    fh.write(str(calcular_cobertura_semanal(usuarios)))
