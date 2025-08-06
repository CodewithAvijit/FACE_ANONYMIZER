from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import mediapipe as mp
from io import BytesIO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

@app.post("/anonymize")
async def anonymize_face(
    file: UploadFile = File(...),
    anonymize: bool = Form(True)
):
    contents = await file.read()
    img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}

    H, W, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out = face_detector.process(img_rgb)

    if out.detections:
        for detection in out.detections:
            bbox = detection.location_data.relative_bounding_box
            x1, y1, w, h = bbox.xmin, bbox.ymin, bbox.width, bbox.height
            x1, y1, w, h = int(x1 * W), int(y1 * H), int(w * W), int(h * H)
            x2, y2 = min(W, x1 + w), min(H, y1 + h)

            if x2 > x1 and y2 > y1:
                if anonymize:
                    img[y1:y2, x1:x2] = cv2.blur(img[y1:y2, x1:x2], (40, 40))
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
                cv2.putText(img, "FACE", (x1 - 50, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 0), 2)

    _, encoded = cv2.imencode(".jpg", img)
    return StreamingResponse(BytesIO(encoded.tobytes()), media_type="image/jpeg")
