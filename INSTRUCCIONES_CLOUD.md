# ☁️ Guía de Despliegue en la Nube (Render.com)

Esta guía te permitirá poner tu Backend (FastAPI) online gratis, para que tu App móvil (Flutter) funcione desde cualquier lugar.

## Paso 1: Subir código a GitHub
1. Crea un repositorio en tu [GitHub](https://github.com/new).
2. Sube la carpeta del proyecto.
   *(Si no sabes usar git, puedes subir los archivos usando la opción "Upload files" de la web de GitHub).*

## Paso 2: Crear el Backend en Render
1. Ve a [dashboard.render.com](https://dashboard.render.com/).
2. Haz clic en **New +** -> **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Configura lo siguiente:
   - **Name**: `ker-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend` (¡Muy importante!)
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
5. Haz clic en **Create Web Service**.

Render te dará una URL (ej: `https://ker-backend.onrender.com`). **¡Cópiala!**

## Paso 3: Conectar la App (Flutter)
1. Abre el archivo `ker_app/lib/services/api.dart`.
2. Busca esta línea y cámbiala por tu URL nueva:
   ```dart
   // api.dart
   return "https://ker-backend.onrender.com"; 
   ```
3. Ejecuta de nuevo tu app: `flutter run -d chrome`.

¡Listo! Tu aplicación ahora consulta la base de datos en la nube.
