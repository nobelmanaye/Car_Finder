from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper.webscrape_cars import find_car
import base64
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/analyze-car")
async def analyze_car(image: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {image.filename}")
        
        # Read image data
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty file received")
            
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Call vehicle identification API
        response = requests.post(
            "https://gemma3-service-800232544942.europe-west4.run.app/v1/chat/completions",
            headers={
                "Authorization": "Bearer YOUR_API_KEY",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma3:4b",
                "messages": [
                    {
                        "role": "system",
                        "content": "Respond ONLY in this JSON format: {\"make\": \"\", \"model\": \"\"}"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Identify vehicle"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "response_format": { "type": "json_object" }
            }
        )
        response.raise_for_status()
        
        vehicle_info = response.json()['choices'][0]['message']['content']
        make = vehicle_info.get('make', '').lower()
        model = vehicle_info.get('model', '').lower()
        
        # Find car listings
        listings = find_car(make, model) if make else None
        
        return {
            "success": True,
            "vehicle": {"make": make, "model": model},
            "listings": listings
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)