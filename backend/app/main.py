from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "System is Live", "port_check": "Successful"}
