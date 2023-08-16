from ultralytics import YOLO
from settings import settings


model = YOLO(settings.MODEL_NAME)
model.fuse()
