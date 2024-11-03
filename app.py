import base64
import os
import logging
from collections import Counter

import numpy as np
from PIL import Image
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

import functions as f
import skin_model as m

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",  # Your frontend application (if any)
    "http://localhost:8000"   # Your FastAPI application
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=JSONResponse)
async def read_root(request: Request):
    logger.info("Serving root endpoint.")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        logger.info("Received image upload request.")
        contents = await file.read()
        print(contents)
        image_data = base64.b64encode(contents).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{image_data}"

        payload = {"image": image_data}
        response_image = await process_image(payload)
        response_lip = await process_lip(payload)

        # Get color recommendations
        color_recommendations = get_color_recommendations(response_image["result"]["result"], response_lip["result"]["result"])

        return JSONResponse(content={
            "response_image": response_image,
            "response_lip": response_lip,
            "color_recommendations": color_recommendations
        })
    except Exception as e:
        logger.error(f"Error processing upload_image: {e}")
        raise HTTPException(status_code=500, detail="fail")

async def process_image(data: dict):
    try:
        logger.info("Processing image for /image endpoint.")

        # Extract and decode the image
        image_data = data["image"]
        decoded_image = base64.b64decode(image_data.split(",")[1])

        # Save the decoded image
        saved_image_path = "saved.jpg"
        with open(saved_image_path, "wb") as fi:
            fi.write(decoded_image)
        logger.info("Image saved as saved.jpg.")

        # Process the saved image to generate a skin mask
        f.save_skin_mask(saved_image_path)
        logger.info("Skin mask saved as temp.jpg.")
        
        # Determine the season from the skin mask
        season_image_path = "temp.jpg"
        ans = m.get_season(season_image_path)

        # Clean up temporary files
        os.remove(season_image_path)
        os.remove(saved_image_path)

        # Adjust the season result according to the mapping
        if ans == 3:
            ans += 1
        elif ans == 0:
            ans = 3

        # Mapping of the season result to season names
        seasons = {1: "spring", 2: "summer", 3: "autumn", 4: "winter"}
        season_name = seasons.get(ans, "unknown")
        
        result = {'result': ans, 'season': season_name}
        logger.info(f"Processed season result: {result}")

        return {"message": "complete", "result": result}
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="fail")

async def process_lip(data: dict):
    try:
        logger.info("Processing image for /lip endpoint.")
        image_data = data["image"]
        decoded_image = base64.b64decode(image_data.split(",")[1])

        with open("saved.jpg", "wb") as fi:
            fi.write(decoded_image)
        logger.info("Image saved as saved.jpg.")

        path = "saved.jpg"
        rgb_codes = f.get_rgb_codes(path)
        random_rgb_codes = f.filter_lip_random(rgb_codes, 40)

        os.remove("saved.jpg")
        logger.info("Processed RGB codes and saved random sample.")

        types = Counter(f.calc_dis(random_rgb_codes))
        max_value_key = max(types, key=types.get)
        logger.info(f"Processed lip result: {max_value_key}")

        # Map the results to the season names
        lip_seasons = {'sp': 'spring', 'su': 'summer', 'au': 'autumn', 'win': 'winter'}
        lip_season = lip_seasons.get(max_value_key, 'unknown')

        result_data = {'result': lip_season}
        return {"message": "complete", "result": result_data}
    except Exception as e:
        logger.error(f"Error processing lip: {e}")
        raise HTTPException(status_code=500, detail="fail")


def get_color_recommendations(skin_tone: int, lip_tone: int):
    # Mapping skin tones and lip tones to color recommendations
    # color_palette = {
    #     1: {
    #         'spring': ["#FFDDC1", "#FFABAB", "#FFC3A0", "#FF677D"],
    #         'summer': ["#E0A899", "#D57A66", "#A26769", "#5D5A5A"],
    #         'autumn': ["#B16B8E", "#A676A7", "#64403E", "#F8AFA6"],
    #         'winter': ["#E5D8BE", "#8A716A", "#594D45", "#413D3D"]
    #     },
    #     2: {
    #         'spring': ["#FFE4E1", "#FF7F50", "#FF6F61", "#B5651D"],
    #         'summer': ["#D6A4A4", "#9C6868", "#6B4B3A", "#3A3A3A"],
    #         'autumn': ["#A39391", "#8B5E83", "#63474D", "#3D3035"],
    #         'winter': ["#FFF5EE", "#C7ADA3", "#A8907B", "#735A57"]
    #     },
    #     3: {
    #         'spring': ["#FFDAB9", "#E6B0AA", "#D5B9B2", "#B16B8E"],
    #         'summer': ["#F5CBA7", "#E59866", "#A569BD", "#5B2C6F"],
    #         'autumn': ["#AAB7B8", "#85929E", "#566573", "#2C3E50"],
    #         'winter': ["#D5D8DC", "#ABB2B9", "#717D7E", "#4D5656"]
    #     },
    #     4: {
    #         'spring': ["#FFEFDB", "#D7BDE2", "#BB8FCE", "#7D3C98"],
    #         'summer': ["#E6E6FA", "#D8BFD8", "#DDA0DD", "#DA70D6"],
    #         'autumn': ["#F5EEF8", "#D2B4DE", "#A569BD", "#633974"],
    #         'winter': ["#F8F9F9", "#E5E8E8", "#CCD1D1", "#979A9A"]
    #     }
    # }
    color_palette = {
    1: {
        'spring': ["#FFDDC1", "#FFE4E1", "#FFB6C1", "#FFC0CB", "#FFDAB9", "#FFEFD5", "#FFF8DC", "#FFFACD", "#FFFFE0", "#FFF5EE"],
        'summer': ["#E0A899", "#FFDAB9", "#F5DEB3", "#FFE4B5", "#FFEFD5", "#FFFACD", "#FFF5EE", "#FFF8DC", "#FAFAD2", "#FFE4C4"],
        'autumn': ["#B16B8E", "#D8BFD8", "#DDA0DD", "#EE82EE", "#DA70D6", "#BA55D3", "#9932CC", "#8A2BE2", "#9400D3", "#8B008B"],
        'winter': ["#E5D8BE", "#D3D3D3", "#C0C0C0", "#A9A9A9", "#808080", "#696969", "#778899", "#708090", "#2F4F4F", "#000000"]
    },
    2: {
        'spring': ["#FFE4E1", "#FFDAB9", "#FFB6C1", "#FFC0CB", "#FFDAB9", "#FFEFD5", "#FFF8DC", "#FFFACD", "#FFFFE0", "#FFF5EE"],
        'summer': ["#D6A4A4", "#F5DEB3", "#FFDAB9", "#FFE4B5", "#FFEFD5", "#FFFACD", "#FFF5EE", "#FFF8DC", "#FAFAD2", "#FFE4C4"],
        'autumn': ["#A39391", "#8B5E83", "#63474D", "#3D3035", "#A52A2A", "#8B0000", "#B22222", "#CD5C5C", "#DC143C", "#FF0000"],
        'winter': ["#FFF5EE", "#D3D3D3", "#C0C0C0", "#A9A9A9", "#808080", "#696969", "#778899", "#708090", "#2F4F4F", "#000000"]
    },
    3: {
        'spring': ["#FFDAB9", "#FFE4E1", "#FFB6C1", "#FFC0CB", "#FFDAB9", "#FFEFD5", "#FFF8DC", "#FFFACD", "#FFFFE0", "#FFF5EE"],
        'summer': ["#F5CBA7", "#F5DEB3", "#FFDAB9", "#FFE4B5", "#FFEFD5", "#FFFACD", "#FFF5EE", "#FFF8DC", "#FAFAD2", "#FFE4C4"],
        'autumn': ["#AAB7B8", "#85929E", "#566573", "#2C3E50", "#A52A2A", "#8B0000", "#B22222", "#CD5C5C", "#DC143C", "#FF0000"],
        'winter': ["#D5D8DC", "#D3D3D3", "#C0C0C0", "#A9A9A9", "#808080", "#696969", "#778899", "#708090", "#2F4F4F", "#000000"]
    },
    4: {
        'spring': ["#FFEFDB", "#FFE4E1", "#FFB6C1", "#FFC0CB", "#FFDAB9", "#FFEFD5", "#FFF8DC", "#FFFACD", "#FFFFE0", "#FFF5EE"],
        'summer': ["#E6E6FA", "#F5DEB3", "#FFDAB9", "#FFE4B5", "#FFEFD5", "#FFFACD", "#FFF5EE", "#FFF8DC", "#FAFAD2", "#FFE4C4"],
        'autumn': ["#F5EEF8", "#D2B4DE", "#A569BD", "#633974", "#A52A2A", "#8B0000", "#B22222", "#CD5C5C", "#DC143C", "#FF0000"],
        'winter': ["#F8F9F9", "#D3D3D3", "#C0C0C0", "#A9A9A9", "#808080", "#696969", "#778899", "#708090", "#2F4F4F", "#000000"]
        }
    }
    
    return color_palette.get(skin_tone, {}).get(lip_tone, [])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="localhost", port=8000, reload=True)
