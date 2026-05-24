from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import base64
import numpy as np

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Incoming frame model
class FrameData(BaseModel):
    image: str

# Face detection API
@app.post("/detect-face")
def detect_face(data: FrameData):

    try:

        # Decode base64 image
        image_data = data.image.split(",")[1]

        img_bytes = base64.b64decode(image_data)

        np_arr = np.frombuffer(img_bytes, np.uint8)

        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Convert grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        results = []

        for (x, y, w, h) in faces:

            results.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            })

        return {
            "faces": results
        }

    except Exception as e:

        return {
            "error": str(e)
        }