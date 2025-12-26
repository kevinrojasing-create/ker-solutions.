# 🚀 Instrucciones de Lanzamiento - KER Solutions MVP

Has recibido el código fuente del MVP de KER Solutions. Sigue estos pasos para levantar el entorno de desarrollo.

## 1. Prerrequisitos
- **Flutter SDK**: Debe estar instalado y en el PATH. Verifica con `flutter doctor`.
- **Python 3.10+**: Para el backend.

## 2. Configuración Inicial (IMPORTANTE)

Como el entorno automatizado no tenía Flutter instalado, debes regenerar los archivos de compilación nativos (Android/iOS/Web).

## 2. Configuración (✅ TODO LISTO)

¡He realizado toda la configuración por ti!
- Backend: Entorno virtual creado y dependencias instaladas.
- Frontend: Proyecto configurado y librerías descargadas.

## 3. Ejecutar la App

### Paso 1: Iniciar Backend
Abre una terminal en `ker_solutions/backend`:
```bash
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 2: Iniciar Frontend (Web)
Abre otra terminal en `ker_solutions/ker_app`:
```bash
C:\Users\kevin\flutter\bin\flutter.bat run -d chrome
```

---
**KER Solutions - Operational Continuity Engine**

## 3. Guía de Uso del MVP

### 🚦 Dashboard Semáforo
- Al iniciar, verás el estado de salud de la tienda.
- **Lógica**: Se conecta al backend para calcular el "Health Score" de 3 activos simulados.
- **Rojo/Amarillo/Verde**: Depende de si los activos están vencidos o sobreusados.

### 🎫 Triage y Tickets
- Toca el botón "Report Issue".
- Simula tomar una foto.
- Al enviar, el Backend ("AI Mock") analiza la severidad.
- Recibirás un mensaje "Ticket Submitted" y el "Triage Started".

### 🔗 Integración Backend
- Asset Health Logic: En `backend/main.py` -> `calculate_asset_health`.
- Triage AI: En `backend/main.py` -> `/triage/analyze`.

---
**KER Solutions - Operational Continuity Engine**
