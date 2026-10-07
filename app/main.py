import os
from fastapi import FastAPI

app = FastAPI()
VERSION = os.getenv("APP_VERSION", "dev")


@app.get("/")
def root():
    return {"message": "Bu sürüm tamamen otomatik deploy edildi!", "version": VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}