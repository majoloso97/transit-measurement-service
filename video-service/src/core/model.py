from ultralytics import YOLO
from settings import settings


def initialize_model(model_name):
    model = YOLO(model_name)
    model.fuse()
    return model

model = initialize_model(settings.MODEL_NAME)
