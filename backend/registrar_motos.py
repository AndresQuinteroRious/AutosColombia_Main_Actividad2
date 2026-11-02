"""Registrar motos en celdas 11-20"""
import requests

api_url = 'http://127.0.0.1:8000'

# Celdas del 11 al 20
celdas = list(range(11, 21))

# Crear celdas si no existen
print("Creando celdas...")
for codigo in celdas:
    try:
        response = requests.post(
            f"{api_url}/celdas",
            json={"codigo": str(codigo), "tipo": "MOTO"}
        )
        if response.status_code == 201:
            print(f"  ✓ Celda {codigo} creada")
        elif response.status_code == 409:
            print(f"  - Celda {codigo} ya existe")
        else:
            print(f"  ✗ Error al crear celda {codigo}: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error al crear celda {codigo}: {e}")

# Obtener las celdas creadas
print("\nObteniendo celdas...")
celdas_response = requests.get(f"{api_url}/celdas?offset=0&limit=100")
celdas_data = celdas_response.json()
celdas_map = {c['codigo']: c['id'] for c in celdas_data['items']}

# Crear vehículos tipo MOTO
print("\nRegistrando motos...")
for codigo in celdas:
    if codigo not in celdas_map:
        print(f"  ✗ Celda {codigo} no encontrada")
        continue
    
    placa = f"MOTO{codigo:02d}"
    try:
        response = requests.post(
            f"{api_url}/vehiculos",
            json={
                "placa": placa,
                "color": "Rojo",
                "modelo": 2025,
                "marca": "Yamaha",
                "tipo": "MOTO",
                "celda_id": celdas_map[str(codigo)]
            }
        )
        if response.status_code == 201:
            vehiculo = response.json()
            print(f"  ✓ Moto {placa} registrada en celda {codigo} (ID: {vehiculo['id']})")
        elif response.status_code == 409:
            print(f"  - Moto {placa} ya existe")
        else:
            print(f"  ✗ Error al registrar moto {placa}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ✗ Error al registrar moto {placa}: {e}")

print("\n¡Registro completado!")
