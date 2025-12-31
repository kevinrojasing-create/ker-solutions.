"""
Minimal FastAPI app for debugging
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="V63 Minimal Debug")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "OK", "message": "Minimal server"}

@app.get("/test")
async def test():
    return {"test": "passed"}
