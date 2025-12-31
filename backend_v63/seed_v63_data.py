"""
Seed V63 with demo data
"""
import asyncio
from sqlalchemy import select
from database import get_db
from sql_models import User, Local, Asset, IoTDevice, DeviceType, AssetStatus, Telemetry
from datetime import datetime
import random

async def seed_data():
    print("Seeding V63 Demo Data...")
    
    async for db in get_db():
        try:
            # 1. Get Owner
            result = await db.execute(select(User).where(User.email == "kevin.rojas.ing@gmail.com"))
            owner = result.scalar_one_or_none()
            
            if not owner:
                print("Error: Owner user not found. Run register_clean.py first.")
                return

            print(f"Assigning data to owner: {owner.full_name}")

            # 2. Create Local
            local = Local(
                owner_id=owner.id,
                name="Oficina Central - Santiago",
                address="Av. Providencia 1234, Oficina 601",
                floor_plan_url="https://example.com/floorplan.jpg"
            )
            db.add(local)
            await db.flush() # Get ID
            print(f"Created Local: {local.name}")

            # 3. Create Assets
            asset1 = Asset(
                local_id=local.id,
                name="Aire Acondicionado Sala Server",
                qr_code="QR-AC-001",
                brand="Samsung",
                model="WindFree",
                status=AssetStatus.OPERATIONAL,
                category="hvac"
            )
            
            asset2 = Asset(
                local_id=local.id,
                name="Refrigerador Laboratorio",
                qr_code="QR-REF-002",
                brand="LG",
                model="Inverter Linear",
                status=AssetStatus.OPERATIONAL,
                category="refrigeration"
            )
            
            db.add(asset1)
            db.add(asset2)
            await db.flush()
            print("Created Assets")

            # 4. Create IoT Device
            sensor = IoTDevice(
                local_id=local.id,
                asset_id=asset1.id,
                device_type=DeviceType.TEMP_HUM,
                device_id="SNZB-02D-TEST-001",
                name="Sensor Temperatura AC Server",
                is_online=True,
                config={"interval": 60}
            )
            db.add(sensor)
            await db.flush()
            print(f"Created IoT Device: {sensor.name}")
            
            # 5. Simulate Telemetry (History)
            print("Generating telemetry history...")
            base_temp = 22.0
            for i in range(10):
                # Fluctuate slightly
                temp = base_temp + random.uniform(-1.0, 1.5)
                hum = random.uniform(45.0, 55.0)
                
                telemetry = Telemetry(
                    device_id=sensor.id,
                    data={"temperature": round(temp, 1), "humidity": round(hum, 1), "battery": 95},
                    timestamp=datetime.now()
                )
                db.add(telemetry)
            
            await db.commit()
            print("✅ Seeding Complete!")
            
        except Exception as e:
            print(f"Seeding failed: {e}")
            await db.rollback()
        break

if __name__ == "__main__":
    asyncio.run(seed_data())
