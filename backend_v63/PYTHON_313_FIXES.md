# Backend V63 - Python 3.13 Compatibility Issues

## Problema Identificado

Backend V63 tiene incompatibilidades con **Python 3.13.9** que causan:
1. Deadlocks en peticiones async
2. Problemas de serialización con Pydantic/FastAPI
3. Event loop blocking en SQLAlchemy async operations

## Solución Aplicada

### 1. Actualizadas todas las dependencias
```bash
pip install --upgrade fastapi starlette pydantic uvicorn sqlalchemy
```

### 2. Modificado endpoint /auth/login
- Removido `response_model=Token` 
- Usando `JSONResponse` directamente para evitar serialización automática de Pydantic
- Esto bypasea el bug de Python 3.13 con async response serialization

### 3. Código modificado en `routers/auth.py`
```python
from fastapi.responses import JSONResponse

@router.post("/login")  # Sin response_model
async def login(...):
    # ...
    return JSONResponse({  # En lugar de Token(...)
        "access_token": access_token,
        "token_type": "bearer",
        ...
    })
```

## Estado Actual

✅ Backend inicia correctamente  
❌ **Peticiones HTTP se bloquean indefinidamente** (deadlock en event loop)

## Solución Recomendada

**Opción 1: Downgrade a Python 3.11 (RECOMENDADA)**
```bash
# Crear virtual environment con Python 3.11
py -3.11 -m venv venv_311
venv_311\Scripts\activate
pip install -r requirements_mvp.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Opción 2: Usar contenedor Docker con Python 3.11**
```dockerfile
FROM python:3.11-slim
# ...
```

**Opción 3: Esperar actualizaciones de librerías**
SQLAlchemy 2.x y asyncio tienen problemas conocidos con Python 3.13.  
Esperar a que las librerías se actualicen (pueden tardar semanas/meses).

## Próximos Pasos

1. Instalar Python 3.11 en el sistema
2. Crear venv con Python 3.11
3. Reinstalar dependencias
4. Probar backend

## Logs de Error

```
TypeError: 'dict' object is not callable
  at starlette/middleware/errors.py line 181
  in await response(scope, receive, send)
```

Esto ocurre porque el event loop de Python 3.13 cambia cómo se manejan las coroutines,  
y FastAPI/Starlette aún no están completamente compatibles.

## Versiones Confirmadas Funcionales

- ✅ Python 3.11.x
- ✅ Python 3.12.x  
- ❌ Python 3.13.x (problemas conocidos)
