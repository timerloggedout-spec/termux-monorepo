# serve_schema.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import pathlib

app = FastAPI(title="Schema Feed Server")

SCHEMA_PATH = pathlib.Path(__file__).parent / "schema_feed.json"

@app.get("/schema")
def get_schema():
    try:
        with open(SCHEMA_PATH, "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
