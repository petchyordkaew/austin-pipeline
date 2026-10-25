"""
The web layer. FastAPI turns ordinary Python functions into HTTP endpoints.

Run it locally (without Docker) with:
    uvicorn app.main:app --reload
then open http://localhost:8000/docs for a clickable test page FastAPI makes for free.
"""

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app import ee


class UTF8JSONResponse(JSONResponse):
    # Say explicitly that the text is UTF-8. Without this, some browsers guess
    # the wrong encoding and the "Ω" symbol shows up as garbage like "Î©".
    media_type = "application/json; charset=utf-8"


app = FastAPI(
    title="Austin's EE API",
    version="0.1.0",
    default_response_class=UTF8JSONResponse,
)


@app.get("/")
def root():
    # APP_VERSION is set by the Dockerfile/CI so you can SEE which build is running.
    # When CD works, pushing a change should make this value change on its own.
    return {
        "message": "EE API is running. Try /docs",
        "version": os.getenv("APP_VERSION", "dev"),
    }


@app.get("/health")
def health():
    # Kubernetes calls this to decide if the container is alive (see k8s/deployment.yaml).
    return {"status": "ok"}


@app.get("/resistor")
def resistor(bands: str = Query(..., examples=["yellow,violet,red,gold"])):
    try:
        return ee.resistor_from_bands(bands.split(","))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ohms-law")
def ohms_law(v: float | None = None, i: float | None = None, r: float | None = None):
    try:
        return ee.ohms_law(v=v, i=i, r=r)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/divider")
def divider(vin: float, r1: float, r2: float):
    try:
        return ee.voltage_divider(vin, r1, r2)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
