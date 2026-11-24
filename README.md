<h1 align="center">🪪 Sistema de Carnets QR & Control de Acceso (FastAPI)</h1>

<p align="center">
  API backend desarrollada en <b>Python</b> con <b>FastAPI</b>, <b>SQLAlchemy</b> y <b>SQLite</b> para el registro de usuarios, generación automática de códigos QR y control/auditoría de accesos en tiempo real.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
</p>

---

## ✨ Características Principales

- 👤 **Registro de Usuarios y Prevención de Duplicados:** Crea usuarios en la base de datos (`midb.db`) validando que el documento sea único y devolviendo códigos de estado HTTP apropiados (`201 Created` / `400 Bad Request`).
- 📷 **Generación Automática de QR:** Al registrar un usuario, genera y guarda su carnet en formato `.png` dentro del directorio `carnets/` usando `qrcode`.
- 🔐 **Validación de Acceso con Reglas de Negocio:** Verifica si el documento existe (`404 Not Found`) y si el carnet está activo (`403 Forbidden` si está bloqueado/inactivo) antes de registrar la entrada.
- 📋 **Historial de Accesos con `INNER JOIN`:** Consulta el registro cronológico de entradas combinando las tablas `usuarios` y `accesos` con marca de tiempo automática.
- 🔗 **Integridad Referencial:** Activa `PRAGMA foreign_keys = ON` en SQLite para garantizar la relación entre usuarios y registros de acceso.

---

## 🛠️ Requisitos e Instalación

1. **Asegúrate de tener Python instalado y descarga las dependencias necesarias:**
   ```bash
   pip install fastapi uvicorn sqlalchemy qrcode pillow
