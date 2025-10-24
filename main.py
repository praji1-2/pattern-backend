# main.py (tolerant parsing version)
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import urllib.parse

app = FastAPI()

API_KEY = "my-secret-key"   # change this to a secure random string

# We accept raw JSON and do our own conversion so empty strings won't 422
class GenerateRequest(BaseModel):
    measurements: dict

def to_float(value, name):
    if value is None or value == "":
        raise ValueError(f"{name} is missing")
    # If it's already a number (int/float), return as float
    if isinstance(value, (int, float)):
        return float(value)
    # If it's a string, strip spaces and attempt conversion
    if isinstance(value, str):
        s = value.strip()
        # allow comma decimal if needed
        s = s.replace(",", ".")
        try:
            return float(s)
        except:
            raise ValueError(f"{name} ('{value}') is not a valid number")
    raise ValueError(f"{name} has invalid type {type(value)}")

def generate_simple_svg(m):
    # expects m as dict with float values
    chest = m["chest"]
    upper_chest = m["upper_chest"]
    waist = m["waist"]
    blouse_length = m["blouse_length"]

    # very small sample SVG using these floats
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='500' height='220'>" \
          f"<rect x='0' y='0' width='500' height='220' fill='white' stroke='black'/>" \
          f"<text x='12' y='24'>Chest: {chest:.2f}</text>" \
          f"<text x='12' y='44'>Upper Chest: {upper_chest:.2f}</text>" \
          f"<text x='12' y='64'>Waist: {waist:.2f}</text>" \
          f"<text x='12' y='84'>Blouse Length: {blouse_length:.2f}</text>" \
          f"</svg>"
    return svg

@app.post("/generate")
async def generate(req: GenerateRequest, request: Request):
    key = request.headers.get("x-api-key", "")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    data = req.measurements
    # Required fields list (tweak if you want other defaults)
    required = ["chest","upper_chest","waist","shoulder","blouse_length","sleeve_length","arm_round","unit"]

    # Convert and validate
    parsed = {}
    errors = []
    for k in required:
        try:
            if k == "unit":
                # unit is a string like "in" or "cm"
                v = data.get(k, "in")
                parsed[k] = str(v).strip()
            else:
                parsed[k] = to_float(data.get(k), k)
        except Exception as e:
            errors.append(str(e))

    if errors:
        # return 400 with readable messages
        raise HTTPException(status_code=400, detail={"errors": errors})

    svg = generate_simple_svg(parsed)
    svg_encoded = urllib.parse.quote(svg, safe='')
    svg_data_url = f"data:image/svg+xml;utf8,{svg_encoded}"
    return {"svg": svg, "svg_data_url": svg_data_url}
