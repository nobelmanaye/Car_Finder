from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import base64
import requests
import logging
import json
import asyncio
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.post("/api/analyze-car")
async def analyze_car(image: UploadFile = File(...)):
    try:
        # File validation
        if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        image_data = await image.read()
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
        
        # Process image
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Call AI service
        response = requests.post(
            "https://gemma3-service-800232544942.europe-west4.run.app/v1/chat/completions",
            headers={
                "Authorization": "Bearer AIzaSyD2-PVdRr7qNSyc1r7HEekltm09CwpMcIQ",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma3:4b",
                "messages": [
                    {
                        "role": "system",
                        "content": """Respond with JSON: {
                            "is_vehicle": boolean,
                            "make": "str", 
                            "model": "str",
                            "confidence": float
                        }"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Is this a vehicle? Identify make and model if yes."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            },
            timeout=30
        )
        
        # Parse response
        vehicle_info = json.loads(response.json()['choices'][0]['message']['content'])
        
        if not vehicle_info.get('is_vehicle', False):
            return {
                "success": False,
                "message": "No vehicle detected",
                "image": f"data:image/jpeg;base64,{base64_image}"
            }
        
        return {
            "success": True,
            "make": vehicle_info.get('make'),
            "model": vehicle_info.get('model'),
            "confidence": vehicle_info.get('confidence'),
            "image": f"data:image/jpeg;base64,{base64_image}"
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)