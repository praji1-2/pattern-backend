from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import urllib.parse

app = FastAPI()

API_KEY = "my-secret-key"  # replace this with a random string later

class Measurements(BaseModel):
    chest: float
    upper_chest: float
    waist: float
    shoulder: float
    blouse_length: float
    sleeve_length: float
    arm_round: float
    unit: str = "in"

class GenerateRequest(BaseModel):
    measurements: Measurements

def generate_simple_svg(m: Measurements):
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='400' height='200'><rect width='400' height='200' fill='white' stroke='black'/><text x='10' y='30'>Pattern for Chest {m.chest}</text></svg>"
    return svg

@app.post("/generate")
async def generate(req: GenerateRequest, request: Request):
    key = request.headers.get("x-api-key", "")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    svg = generate_simple_svg(req.measurements)
    svg_encoded = urllib.parse.quote(svg, safe='')
