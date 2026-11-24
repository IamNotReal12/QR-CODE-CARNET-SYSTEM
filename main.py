import sqlalchemy
import os
import qrcode
from fastapi import HTTPException, status, FastAPI, Depends

URL_DB = "sqlite:///./midb.db"


engine = sqlalchemy.create_engine(
    URL_DB, connect_args={"check_same_thread": False}, echo=True
)


def init_db():
    with engine.begin() as conn:

        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                documento VARCHAR(100) UNIQUE NOT NULL,
                rol VARCHAR(50) NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1
            )
        """))

        conn.execute(sqlalchemy.text("""
            CREATE TABLE IF NOT EXISTS accesos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """))


init_db()


def get_db():
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("PRAGMA foreign_keys = ON;"))
        yield conn


class Usuario:
    def __init__(self, id: int, nombre: str, documento: str, rol: str, activo: int = 1):
        self.id = id
        self.nombre = nombre
        self.documento = documento
        self.rol = rol
        self.activo = activo


class SistemaCarnet:
    def __init__(self, carpeta_carnets: str = "carnets"):
        self.carpeta_carnets = carpeta_carnets

        os.makedirs(self.carpeta_carnets, exist_ok=True)

    def generar_qr(self, documento: str) -> str:
        qr = qrcode.QRCode(
            border=4, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M
        )
        qr.add_data(documento)
        imagen_qr = qr.make_image(fill_color="#000000", back_color="#ffffff")

        ruta_archivo = f"{self.carpeta_carnets}/carnet_{documento}.png"
        imagen_qr.save(ruta_archivo)

        return ruta_archivo

    def registrar_usuario(
        self, conn: sqlalchemy.engine.Connection, nombre: str, documento: str, rol: str
    ):
        query = """SELECT nombre FROM usuarios WHERE documento = :documento_ref"""

        resultado = conn.execute(
            sqlalchemy.text(query), {"documento_ref": documento}
        ).first()

        if resultado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario registrado con ese documento",
            )
        nuevo_registro = conn.execute(
            sqlalchemy.text(
                "INSERT INTO usuarios (nombre, documento, rol) VALUES (:nombre, :documento, :rol)"
            ),
            {"nombre": nombre, "documento": documento, "rol": rol},
        )
        ruta_qr = self.generar_qr(documento)
        nuevo_usuario = Usuario(
            id=nuevo_registro.lastrowid, nombre=nombre, documento=documento, rol=rol
        )

        return {"usuario": nuevo_usuario, "qr_ruta": ruta_qr}

    def validar_acceso(self, conn: sqlalchemy.engine.Connection, documento: str):
        query = """SELECT id, nombre, rol, activo FROM usuarios WHERE documento = :documento"""
    
        usuario = conn.execute(
            sqlalchemy.text(query), {"documento": documento}
        ).first()

        if not usuario:
            raise HTTPException(
                status_code=404, detail="Carnet inválido: usuario no encontrado"
            )
        if usuario.activo == 0:
            raise HTTPException(
                status_code=403, detail="Acceso denegado: carnet bloqueado o inactivo"
            )

        conn.execute(
            sqlalchemy.text("INSERT INTO accesos (usuario_id) VALUES (:usuario_id)"),
            {"usuario_id": usuario.id},
        )
        return {
            "mensaje": "Acceso permitido. ¡Bienvenido!",
            "usuario": usuario.nombre,
            "rol": usuario.rol,
        }


app = FastAPI(title="Sistema de Carnets QR")
sistema = SistemaCarnet()


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def crear_usuario(
    nombre: str,
    documento: str,
    rol: str,
    conn: sqlalchemy.engine.Connection = Depends(get_db),
):
    return sistema.registrar_usuario(conn, nombre, documento, rol)


@app.post("/acceso/{documento}")
def registrar_entrada(
    documento: str, conn: sqlalchemy.engine.Connection = Depends(get_db)
):
    return sistema.validar_acceso(conn, documento)


@app.get("/accesos")
def listar_accesos(conn: sqlalchemy.engine.Connection = Depends(get_db)):
    query = """
        SELECT 
            accesos.id AS acceso_id,
            usuarios.nombre,
            usuarios.documento,
            usuarios.rol,
            accesos.fecha_hora
        FROM accesos
        INNER JOIN usuarios ON accesos.usuario_id = usuarios.id
        ORDER BY accesos.fecha_hora DESC
    """
    filas = conn.execute(sqlalchemy.text(query)).all()
    
    if not filas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tabla vacia"
        )
    return [dict(fila._mapping) for fila in filas]