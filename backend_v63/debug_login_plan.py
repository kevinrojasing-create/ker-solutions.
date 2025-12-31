import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_flow():
    email = "debug_user@test.com"
    password = "password123"
    
    print(f"1. Intentando registrar usuario de prueba: {email}")
    try:
        reg_response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Debug User",
            "company_name": "Debug Corp",
            "role": "owner",
            "plan": "monitor_360"
        })
        
        if reg_response.status_code in [200, 201]:
            print("   ✅ Registro exitoso.")
        elif reg_response.status_code == 400 and "already registered" in reg_response.text:
            print("   ⚠️ Usuario ya existe (continuando...)")
        else:
            print(f"   ❌ Error en registro: {reg_response.status_code} - {reg_response.text}")
            return

        print(f"\n2. Intentando LOGIN con: {email}")
        auth_response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": email,
            "password": password
        }) # FastAPI OAuth2FormRequest usa form-data, pero nuestro endpoint custom usa JSON o form dependiendo de la implementación.
        
        # Revisemos auth.py: ¿Usa OAuth2PasswordRequestForm o LoginRequest (JSON)?
        # Si usa OAuth2PasswordRequestForm, espera form-data 'username' y 'password'.
        # Si probamos con JSON:
        json_auth_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if json_auth_response.status_code == 200:
            data = json_auth_response.json()
            print("   ✅ Login exitoso (JSON Endpoint).")
            print("   📦 Respuesta del servidor:")
            print(json.dumps(data, indent=2))
            
            user_plan = data.get('user', {}).get('plan')
            if user_plan:
                print(f"   🎉 CAMPO PLAN DETECTADO: {user_plan}")
            else:
                print("   ❌ ERROR: El campo 'plan' no viene en la respuesta del usuario.")
        else:
            print(f"   ❌ Error en Login: {json_auth_response.status_code} - {json_auth_response.text}")

    except Exception as e:
        print(f"   ❌ Excepción al conectar: {e}")

if __name__ == "__main__":
    test_login_flow()
