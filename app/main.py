import os
import time
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
VERSION = os.getenv("APP_VERSION", "dev")

Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {"message": "Bu sürüm tamamen otomatik deploy edildi!", "version": VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/slow")
def slow():
    time.sleep(0.5)
    return {"status": "yavas ama calisiyor"}


@app.get("/error")
def error():
    raise HTTPException(status_code=500, detail="Bilerek uretilmis hata")