# Alembic Setup Guide - V62 Enterprise Master

## ✅ What's Been Done

1. **Alembic Initialized** with async template
2. **env.py Configured** to recognize all 65+ V62 tables
3. **Database imports** properly set up

## ⚠️ Dependency Installation Issue

The automatic installation of dependencies encountered an error with Python 3.13. This is a known compatibility issue with some packages.

## 🔧 Manual Setup Steps

### Step 1: Install Dependencies

Try one of these approaches:

**Option A: Use Python 3.11 or 3.12 (Recommended)**
```bash
# Install Python 3.11 or 3.12
# Then create a new virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option B: Install packages individually**
```bash
pip install fastapi uvicorn sqlalchemy alembic asyncpg
pip install python-jose passlib python-multipart
pip install pydantic-settings python-dotenv httpx python-dateutil
pip install gunicorn psycopg2-binary
```

### Step 2: Create .env File

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ker_v62
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Step 3: Generate Migration

```bash
python -m alembic revision --autogenerate -m "Initial V62 Schema - Complete Enterprise Master"
```

This should create a file like `alembic/versions/xxxxx_initial_v62_schema.py` with all 65+ tables.

### Step 4: Apply Migration

```bash
python -m alembic upgrade head
```

This will create all tables in your PostgreSQL database.

### Step 5: Verify

```bash
# Check migration status
python -m alembic current

# Check database tables
psql -d ker_v62 -c "\dt"
```

You should see all 65+ tables created.

---

## 🐛 Troubleshooting

### Error: "No module named 'pydantic_settings'"
```bash
pip install pydantic-settings
```

### Error: "No module named 'asyncpg'"
```bash
pip install asyncpg
```

### Error: "Can't locate revision identified by 'xxxxx'"
```bash
# Reset alembic
rm -rf alembic/versions/*
python -m alembic revision --autogenerate -m "Initial V62 Schema"
python -m alembic upgrade head
```

### Error: Database connection refused
```bash
# Make sure PostgreSQL is running
# Check DATABASE_URL in .env
# Test connection:
psql -d ker_v62
```

---

## 📊 Expected Migration Output

When you run the autogenerate command, you should see:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'system_settings'
INFO  [alembic.autogenerate.compare] Detected added table 'plan_limits'
INFO  [alembic.autogenerate.compare] Detected added table 'app_versions'
INFO  [alembic.autogenerate.compare] Detected added table 'users'
... (60+ more tables)
  Generating /path/to/alembic/versions/xxxxx_initial_v62_schema.py ...  done
```

---

## 🎯 Next Steps After Migration

Once the migration is successful:

1. **Seed Data** - Create initial system settings, default risk matrix, etc.
2. **Test API** - Run `uvicorn main:app --reload`
3. **Create First User** - Use `/auth/register` endpoint
4. **Build Routers** - Start implementing API endpoints

---

## 📝 Alembic Commands Reference

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history

# Rollback to specific version
alembic downgrade <revision_id>
```

---

## ✅ Verification Checklist

- [ ] All dependencies installed
- [ ] .env file created with DATABASE_URL
- [ ] PostgreSQL database created
- [ ] Migration generated successfully
- [ ] Migration applied (alembic upgrade head)
- [ ] All 65+ tables visible in database
- [ ] FastAPI server starts without errors

---

**Status:** Alembic configured, awaiting dependency installation  
**Action Required:** Install dependencies and run migration commands manually
