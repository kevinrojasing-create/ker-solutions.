"""
Minimal test server to verify FastAPI and uvicorn work correctly
"""
from fastapi import FastAPI

app = FastAPI(title="V63 Test")

@app.get("/")
def root():
    return {"status": "OK", "message": "Basic server working"}

@app.get("/test")
def test():
    return {"test": "passed"}
