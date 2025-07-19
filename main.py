from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dbfread import DBF
from dbf import Table, READ_WRITE
from datetime import datetime
import os

# ================================
# CONFIGURACIÓN FASTAPI
# ================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# ARCHIVOS DBF
# ================================
ZETH50T = "ZETH50T.DBF"
ZETH51T = "ZETH51T.DBF"
ZETH70 = "ZETH70.DBF"
ZETH70_EXT = "ZETH70_EXT.DBF"
HISTORICO_DBF = "VENTAS_HISTORICO.DBF"

# ✅ Solo los campos que pediste
CAMPOS_HISTORICO = (
    "EERR C(20);"
    "EERR_CONC C(30);"
    "FECHA D;"
    "N_TICKET C(10);"
    "NOMBRES C(50);"
    "TIPO C(5);"
    "CANT N(6,0);"
    "PROD_SERV C(50);"
    "P_UNIT N(12,2);"
    "CATEGORIA C(20);"
    "SUB_CAT C(20);"
    "COST_UNIT N(12,2);"
    "PRONUM C(10);"
    "DESCRI C(50)"
)

# ================================
# FUNCIONES AUXILIARES
# ================================
def crear_dbf_historico():
    if not os.path.exists(HISTORICO_DBF):
        table = Table(HISTORICO_DBF, CAMPOS_HISTORICO, codepage="cp850")
        table.open(mode=READ_WRITE)
        table.close()
        print("✅ VENTAS_HISTORICO.DBF creado.")

def leer_dbf_existente():
    if not os.path.exists(HISTORICO_DBF):
        return set()
    return {r["N_TICKET"] for r in DBF(HISTORICO_DBF, load=True, encoding="cp850")}

def agregar_al_historico(nuevos_registros):
    table = Table(HISTORICO_DBF)
    table.open(mode=READ_WRITE)
    for reg in nuevos_registros:
        table.append(reg)
    table.close()

def obtener_costo_producto(pronum, productos):
    producto = productos.get(pronum)
    if producto:
        return float(producto.get("ULCOSREP", 0.0))
    return 0.0

# ================================
# ENDPOINT RAÍZ
# ================================
@app.get("/")
def home():
    return {
        "mensaje": "✅ API activa en Render",
        "usar_endpoint": "/reporte → Devuelve datos filtrados",
        "descargar": "/descargar/historico"
    }

# ================================
# ENDPOINT PRINCIPAL OPTIMIZADO
# ================================
@app.get("/reporte")
def generar_reporte():
    try:
        # Verificar existencia de archivos
        for archivo in [ZETH50T, ZETH51T, ZETH70]:
            if not os.path.exists(archivo):
                return {"error": f"No se encontró {archivo}"}

        crear_dbf_historico()
        tickets_existentes = leer_dbf_existente()

        productos = {r["PRONUM"]: r for r in DBF(ZETH70, load=True, encoding="cp850")}
        productos_ext = (
            {r["PRONUM"]: r for r in DBF(ZETH70_EXT, load=True, encoding="cp850")}
            if os.path.exists(ZETH70_EXT)
            else {}
        )
        cabeceras = {r["NUMCHK"]: r for r in DBF(ZETH50T, load=True, encoding="cp850")}

        # ✅ Filtro de fecha
        fecha_inicio = datetime(2025, 3, 1)
        fecha_hoy = datetime.today()

        nuevos_registros, datos_respuesta = [], []

        for detalle in DBF(ZETH51T, load=True, encoding="cp850"):
            numchk = detalle["NUMCHK"]

            if numchk in tickets_existentes:
                continue

            cab = cabeceras.get(numchk)
            if not cab:
                continue

            fecchk = cab.get("FECCHK")
            if not isinstance(fecchk, datetime) or not (fecha_inicio <= fecchk <= fecha_hoy):
                continue

            pronum = detalle.get("PRONUM", "")
            prod_ext = productos_ext.get(pronum, {})
            cost_unit = obtener_costo_producto(pronum, productos)

            cant = float(detalle.get("CANT", 0))
            p_unit = float(detalle.get("QTYPRO", 0))

            nuevo = {
                "EERR": prod_ext.get("EERR", ""),
                "EERR_CONC": "CREDITO" if cab.get("TYPPMOV", "") == "C" else "CONTADO",
                "FECHA": fecchk,
                "N_TICKET": cab.get("NUMCHK", ""),
                "NOMBRES": cab.get("CUSNAM", ""),
                "TIPO": cab.get("TYPPAG", ""),
                "CANT": cant,
                "PROD_SERV": detalle.get("PROD_SERV", ""),
                "P_UNIT": p_unit,
                "CATEGORIA": prod_ext.get("CATEGORIA", ""),
                "SUB_CAT": prod_ext.get("SUB_CAT", ""),
                "COST_UNIT": cost_unit,
                "PRONUM": pronum,
                "DESCRI": prod_ext.get("DESCRI", "")
            }

            nuevos_registros.append(nuevo)
            datos_respuesta.append(nuevo)

        if nuevos_registros:
            agregar_al_historico(nuevos_registros)

        return {"total": len(datos_respuesta), "datos": datos_respuesta}

    except Exception as e:
        return {"error": str(e)}

# ================================
# ENDPOINT PARA DESCARGAR HISTÓRICO
# ================================
@app.get("/descargar/historico")
def descargar_historico():
    if not os.path.exists(HISTORICO_DBF):
        return {"error": "El archivo histórico aún no existe."}
    return FileResponse(
        HISTORICO_DBF,
        media_type="application/octet-stream",
        filename=HISTORICO_DBF
    )










