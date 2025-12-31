# KER Solutions V63 - Simplified SaaS + IoT

## 🎯 Overview

KER Solutions V63 is a simplified, production-ready SaaS platform for facility management with integrated IoT monitoring. This version focuses on core functionality while maintaining enterprise-grade reliability.

### Key Features

- ✅ **Multi-tenant Architecture** - Secure isolation per location
- ✅ **IoT Integration** - Real-time monitoring with Zigbee & WiFi sensors
- ✅ **Smart Alerts** - AI-powered anomaly detection
- ✅ **Asset Management** - Digital inventory with QR codes
- ✅ **Service Tickets** - Complete maintenance workflow
- ✅ **Dashboard Analytics** - Energy & climate metrics

## 🏗️ Architecture

### Database Models (11 Tables)

**Core:**
- `users` - Multi-role user management
- `locales` - Physical locations (multi-tenant)
- `local_members` - User access control
- `otp_codes` - Email verification

**Operations:**
- `assets` - Equipment & machinery
- `service_tickets` - Maintenance tickets
- `ticket_attachments` - Photos/documents

**IoT:**
- `iot_devices` - Sensor registry
- `telemetry` - Time-series data
- `alerts` - AI-generated alerts
- `audit_logs` - Audit trail

### Supported IoT Hardware

1. **Zigbee Bridge Pro** - Gateway/Hub
   - Connects Zigbee sensors to cloud via WiFi
   - Parent node for all SNZB sensors

2. **POW Origin** - Energy Monitor (WiFi)
   - Voltage, current, power (kW) measurement
   - Detects motor stress & energy spikes
   - Installed on critical assets (refrigerators, AC units)

3. **SNZB-02D** - Temp/Humidity Sensor (Zigbee)
   - LCD display for local reading
   - Cold chain monitoring
   - Generates critical temperature alerts

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ (production) or SQLite (development)

### Installation

```bash
cd backend_v63

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Initialize database
alembic upgrade head

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

```env
# App
APP_NAME=KER Solutions V63
APP_VERSION=63.0.0
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite+aiosqlite:///./ker_v63.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ker_v63

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 📡 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with JWT
- `POST /auth/verify-otp` - Verify OTP code
- `POST /auth/password-reset/request` - Request password reset
- `POST /auth/password-reset/confirm` - Confirm reset with OTP

### Locales
- `GET /locales` - List accessible locales
- `POST /locales` - Create new local
- `GET /locales/{id}` - Get local details
- `PUT /locales/{id}` - Update local
- `DELETE /locales/{id}` - Delete local
- `GET /locales/{id}/members` - List members
- `POST /locales/{id}/members` - Add member
- `DELETE /locales/{id}/members/{user_id}` - Remove member

### Assets
- `GET /assets` - List assets
- `POST /assets` - Create asset
- `GET /assets/{id}` - Get asset details
- `PUT /assets/{id}` - Update asset
- `DELETE /assets/{id}` - Delete asset
- `GET /assets/{id}/health` - Get health score

### Tickets
- `GET /tickets` - List tickets
- `POST /tickets` - Create ticket
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket
- `POST /tickets/{id}/assign` - Assign technician
- `POST /tickets/{id}/complete` - Complete ticket
- `POST /tickets/{id}/attachments` - Upload file

### IoT
- `GET /iot/devices` - List IoT devices
- `POST /iot/devices` - Register device
- `GET /iot/devices/{id}` - Get device details
- `PUT /iot/devices/{id}` - Update device config
- `POST /iot/telemetry` - Receive sensor data (webhook)
- `GET /iot/telemetry/{device_id}` - Get telemetry history

### Alerts
- `GET /alerts` - List alerts
- `GET /alerts/{id}` - Get alert details
- `PUT /alerts/{id}/acknowledge` - Acknowledge alert
- `PUT /alerts/{id}/resolve` - Resolve alert

### Dashboard
- `GET /dashboard/stats` - General statistics
- `GET /dashboard/energy` - Energy consumption metrics
- `GET /dashboard/climate` - Temperature/humidity metrics

## 🔧 Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

## 📊 IoT Data Flow

```
SNZB-02D Sensor → Zigbee Bridge Pro → WiFi → KER Cloud
POW Origin Sensor → WiFi → KER Cloud

KER Cloud:
1. Receives telemetry via POST /iot/telemetry
2. Stores in database
3. Checks alert rules
4. Generates alerts if thresholds exceeded
5. Sends push notifications to app
```

### Alert Rules Example

```python
# Temperature high alert
if temperature > config["temp_threshold_high"]:
    create_alert(
        type="temperature_high",
        severity="critical",
        message=f"Temp {temp}°C exceeds {threshold}°C"
    )

# Energy spike alert
if energy > config["energy_threshold"]:
    create_alert(
        type="energy_spike",
        severity="warning",
        message=f"Consumption {energy}kW exceeds {threshold}kW"
    )
```

## 🚢 Deployment

### Render.com (Recommended)

```yaml
# render.yaml
services:
  - type: web
    name: ker-v63-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ker-v63-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Comparison: V62 vs V63

| Feature | V62 | V63 |
|---------|-----|-----|
| Database Tables | 52 | 11 |
| Code Lines (models) | 1795 | ~500 |
| Development Time | 10 weeks | 1-2 weeks |
| IoT Support | Models only | Fully functional |
| Complexity | Enterprise | MVP SaaS |
| Target Market | Multi-industry | SMB with IoT |

## 🔐 Security

- ✅ JWT authentication with bcrypt password hashing
- ✅ Role-based access control (RBAC)
- ✅ Multi-tenant data isolation
- ✅ Audit logging
- ✅ CORS configuration
- ✅ SQL injection prevention (ORM)

## 📝 License

Proprietary - KER Solutions © 2025

## 🤝 Support

For support, email support@kersolutions.com

---

**KER Solutions V63 - Tranquilidad para la continuidad de su negocio** ✨
