import onnxruntime as ort
import numpy as np
from PIL import Image
from ultralytics import YOLO

# Load model Large đã train (ONNX)
session = ort.InferenceSession("best.onnx", providers=["CPUExecutionProvider"])
names = YOLO("best.pt").names

def preprocess(image):
    img = image.convert("RGB").resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, axis=0)
    return arr

def predict(image):
    inputs = {session.get_inputs()[0].name: preprocess(image)}
    outputs = session.run(None, inputs)[0]
    pred_class_id = int(np.argmax(outputs))
    pred_score = float(np.max(outputs))
    return names[pred_class_id], pred_score
