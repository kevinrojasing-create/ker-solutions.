# KER Solutions V63 - Migration Guide from V62

## Overview

This guide helps you understand the differences between V62 and V63 and how to migrate if needed.

## Key Differences

### Database Schema

**V62 (52 tables):**
- Complete enterprise feature set
- BIM, IoT (complex), LMS, VMS, ESG modules
- Finance, Procurement, Quality modules
- 1795 lines of model code

**V63 (11 tables):**
- Core operations only
- Simplified IoT with real implementation
- Focus on SMB market
- ~500 lines of model code

### Removed Features (Not in V63)

- ❌ BIM integration
- ❌ Learning Management System (LMS)
- ❌ Visitor Management System (VMS)
- ❌ ESG tracking
- ❌ Advanced procurement
- ❌ Financial modules
- ❌ Quality audits
- ❌ Complex workflows

### New/Improved in V63

- ✅ **Functional IoT** - Real integration with Zigbee Bridge Pro, POW Origin, SNZB-02D
- ✅ **Smart Alerts** - AI-powered anomaly detection from telemetry
- ✅ **Dashboard Metrics** - Energy & climate statistics
- ✅ **Simplified API** - Easier to integrate and maintain
- ✅ **Faster Development** - 1-2 weeks vs 10 weeks

## Migration Path

### Option 1: Fresh Start (Recommended)

If you're starting a new project or can afford data migration:

1. Deploy V63 backend
2. Configure IoT devices
3. Register assets manually or via import script
4. Train users on new simplified interface

### Option 2: Gradual Migration

If you have existing V62 data:

1. Keep V62 running
2. Deploy V63 in parallel
3. Migrate core data (users, locales, assets)
4. Redirect new operations to V63
5. Archive V62 after transition period

### Data Migration Script

```python
# migrate_v62_to_v63.py
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connect to both databases
v62_engine = create_engine("sqlite:///ker_v62.db")
v63_engine = create_engine("sqlite:///ker_v63.db")

async def migrate_users():
    # Migrate users (simplified roles)
    pass

async def migrate_locales():
    # Migrate locales
    pass

async def migrate_assets():
    # Migrate assets (simplified fields)
    pass

# Run migration
asyncio.run(migrate_all())
```

## IoT Device Setup

### Hardware Required

1. **Zigbee Bridge Pro** (~$30)
   - One per location
   - Connects to WiFi router

2. **POW Origin** (~$25 each)
   - One per critical asset (refrigerator, AC, etc.)
   - Measures energy consumption

3. **SNZB-02D** (~$10 each)
   - Multiple per location
   - Temperature/humidity monitoring

### Configuration Steps

1. **Register Bridge**
```bash
POST /iot/devices
{
  "local_id": 1,
  "device_type": "bridge",
  "device_id": "BRIDGE-MAC-ADDRESS",
  "name": "Main Bridge",
  "config": {}
}
```

2. **Register Sensors**
```bash
POST /iot/devices
{
  "local_id": 1,
  "device_type": "temp_hum",
  "device_id": "SNZB-MAC-ADDRESS",
  "name": "Refrigerator Sensor",
  "asset_id": 5,
  "config": {
    "temp_threshold_high": 8,
    "temp_threshold_low": 2
  }
}
```

3. **Configure Webhooks**

Point your IoT platform to send data to:
```
POST https://your-api.com/iot/telemetry
{
  "device_id": 123,
  "data": {
    "temperature": 23.5,
    "humidity": 65
  }
}
```

## API Changes

### Removed Endpoints

All endpoints from removed modules:
- `/training/*`
- `/visitors/*`
- `/procurement/*`
- `/finance/*`
- `/quality/*`
- `/bim/*`

### New Endpoints

- `GET /dashboard/energy` - Energy metrics
- `GET /dashboard/climate` - Climate metrics
- `POST /iot/telemetry` - Receive sensor data
- `GET /iot/telemetry/{device_id}` - Get history

## Recommendations

### When to Use V62

- Large enterprise with complex needs
- Multiple departments requiring specialized modules
- Budget for 10+ weeks of development
- Need for BIM, LMS, VMS integration

### When to Use V63

- SMB (Small/Medium Business)
- Focus on core operations + IoT monitoring
- Need to launch quickly (1-2 weeks)
- Budget-conscious
- Want proven, simple architecture

## Support

For migration assistance, contact support@kersolutions.com

---

**Recommendation:** For new projects, start with V63. You can always add features later as your business grows.
