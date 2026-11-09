"""Genera el JPG del diagrama de clases del backend."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SALIDA = Path(__file__).with_name("diagrama_clases.jpg")
ANCHO, ALTO = 3000, 1900
IMAGEN = Image.new("RGB", (ANCHO, ALTO), "#f4f7fb")
DIBUJO = ImageDraw.Draw(IMAGEN)
FUENTE_DIR = Path("C:/Windows/Fonts")
FUENTE = ImageFont.truetype(str(FUENTE_DIR / "segoeui.ttf"), 25)
FUENTE_BOLD = ImageFont.truetype(str(FUENTE_DIR / "segoeuib.ttf"), 31)
FUENTE_TITULO = ImageFont.truetype(str(FUENTE_DIR / "segoeuib.ttf"), 48)

AZUL = "#173b63"
TEXTO = "#203247"
LINEA = "#55718e"
ACENTO = "#dcecff"
BLANCO = "#ffffff"

DIBUJO.text((100, 55), "Autos Colombia | Diagrama de clases", font=FUENTE_TITULO, fill=AZUL)
DIBUJO.text((102, 120), "Entidades SQLAlchemy y relaciones por claves foráneas", font=FUENTE, fill="#50657b")


def caja(x, y, ancho, titulo, atributos, metodos=()):
    margen = 24
    alto = 105 + len(atributos) * 39 + (22 + len(metodos) * 39 if metodos else 0)
    DIBUJO.rounded_rectangle((x, y, x + ancho, y + alto), radius=18, fill=BLANCO, outline=AZUL, width=4)
    DIBUJO.rounded_rectangle((x, y, x + ancho, y + 76), radius=16, fill=ACENTO)
    DIBUJO.rectangle((x, y + 58, x + ancho, y + 76), fill=ACENTO)
    DIBUJO.text((x + margen, y + 18), titulo, font=FUENTE_BOLD, fill=AZUL)
    cursor = y + 91
    for atributo in atributos:
        DIBUJO.text((x + margen, cursor), atributo, font=FUENTE, fill=TEXTO)
        cursor += 39
    if metodos:
        cursor += 9
        DIBUJO.line((x + margen, cursor, x + ancho - margen, cursor), fill="#c7d3df", width=2)
        cursor += 12
        for metodo in metodos:
            DIBUJO.text((x + margen, cursor), metodo, font=FUENTE, fill=TEXTO)
            cursor += 39
    return (x, y, x + ancho, y + alto)


def relacion(inicio, fin, etiqueta, puntos=None, etiqueta_xy=None):
    if puntos is None:
        puntos = [inicio, fin]
    DIBUJO.line(puntos, fill=LINEA, width=4, joint="curve")
    x, y = fin
    DIBUJO.ellipse((x - 8, y - 8, x + 8, y + 8), fill=LINEA)
    if etiqueta_xy:
        DIBUJO.text(etiqueta_xy, etiqueta, font=FUENTE, fill=AZUL, stroke_width=4, stroke_fill="#f4f7fb")


# Entidades con vínculos, distribuidas para que las asociaciones sean visibles.
vehiculo = caja(130, 270, 650, "Vehiculo", [
    "id: int [PK]", "placa, color, modelo, marca, tipo: datos", "celda_id: int | NULL [FK]", "celda: Celda | None",
], ["validate_text()", "validate_modelo()"])
celda = caja(2220, 270, 650, "Celda", ["id: int [PK]", "codigo: str", "tipo: str"], ["validate_text()"])
estancia = caja(1060, 600, 850, "Estancia", [
    "id: int [PK]", "vehiculo_id, celda_id: int [FK]", "entrada: datetime", "salida: datetime | None",
    "operador_entrada_id: int [FK]", "operador_salida_id: int | None [FK]",
    "vehiculo, celda, operador_entrada, operador_salida",
], ["esta_abierta()", "cerrar(fecha_salida, operador)"])
operador = caja(1110, 175, 750, "Operador", [
    "id: int [PK]", "nombre, telefono: str", "direccion: str | NULL",
], ["validate_text()"])
cuenta = caja(2220, 1110, 650, "Cuenta", [
    "id: int [PK]", "usuario: str [único]", "password_hash, rol: str", "operador_id: int | NULL [FK]",
])
usuario = caja(130, 1120, 650, "Usuario", [
    "id: int [PK]", "nombre, documento, telefono: str", "fecha_vencimiento: date", "rol, turno: str",
    "horas_semana, ausentismo_horas: int",
], ["horas_disponibles()", "cobertura_semanal()", "mensualidad_vigente()"])
pago = caja(1060, 1250, 500, "Pago", [
    "id: int [PK]", "valor: Decimal", "fecha: datetime", "periodo: str",
], ["validate_valor()", "validate_text()"])
novedad = caja(1650, 1250, 500, "Novedad", [
    "id: int [PK]", "descripcion: str", "fecha: datetime",
], ["validate_text()"])

# Las líneas se dibujan tras las cajas para que los nodos queden sobre los conectores.
relacion((780, 445), (2220, 445), "0..* vehículos / 0..1 celda", [(780, 445), (970, 445), (970, 510), (2070, 510), (2070, 445), (2220, 445)], (1100, 465))
relacion((780, 600), (1060, 710), "0..* estancias / 1 vehículo", [(780, 600), (900, 600), (900, 710), (1060, 710)], (800, 615))
relacion((2220, 600), (1910, 785), "0..* estancias / 1 celda", [(2220, 600), (2070, 600), (2070, 785), (1910, 785)], (1930, 610))
relacion((1480, 600), (1480, 455), "entrada: 1 operador", [(1480, 600), (1480, 455)], (1500, 500))
relacion((1650, 600), (1770, 455), "salida: 0..1 operador", [(1650, 600), (1770, 500), (1770, 455)], (1680, 510))
relacion((2220, 1250), (1820, 455), "0..* cuentas / 0..1 operador", [(2220, 1250), (2140, 1250), (2140, 160), (1820, 160), (1820, 455)], (1900, 135))

# Repinta las cajas y su contenido sobre las líneas de asociación.
caja(130, 270, 650, "Vehiculo", ["id: int [PK]", "placa, color, modelo, marca, tipo: datos", "celda_id: int | NULL [FK]", "celda: Celda | None"], ["validate_text()", "validate_modelo()"])
caja(2220, 270, 650, "Celda", ["id: int [PK]", "codigo: str", "tipo: str"], ["validate_text()"])
caja(1060, 600, 850, "Estancia", ["id: int [PK]", "vehiculo_id, celda_id: int [FK]", "entrada: datetime", "salida: datetime | None", "operador_entrada_id: int [FK]", "operador_salida_id: int | None [FK]", "vehiculo, celda, operador_entrada, operador_salida"], ["esta_abierta()", "cerrar(fecha_salida, operador)"])
caja(1110, 175, 750, "Operador", ["id: int [PK]", "nombre, telefono: str", "direccion: str | NULL"], ["validate_text()"])
caja(2220, 1110, 650, "Cuenta", ["id: int [PK]", "usuario: str [único]", "password_hash, rol: str", "operador_id: int | NULL [FK]"])
caja(130, 1120, 650, "Usuario", ["id: int [PK]", "nombre, documento, telefono: str", "fecha_vencimiento: date", "rol, turno: str", "horas_semana, ausentismo_horas: int"], ["horas_disponibles()", "cobertura_semanal()", "mensualidad_vigente()"])
caja(1060, 1250, 500, "Pago", ["id: int [PK]", "valor: Decimal", "fecha: datetime", "periodo: str"], ["validate_valor()", "validate_text()"])
caja(1650, 1250, 500, "Novedad", ["id: int [PK]", "descripcion: str", "fecha: datetime"], ["validate_text()"])

DIBUJO.text((130, 1780), "PK: clave primaria  |  FK: clave foránea  |  Las cardinalidades indican relaciones permitidas por el modelo.", font=FUENTE, fill="#50657b")
IMAGEN.save(SALIDA, format="JPEG", quality=94, subsampling=0, optimize=True)
print(SALIDA)
