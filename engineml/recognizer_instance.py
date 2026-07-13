from django.conf import settings
from .recognizer import ActivityRecognizer

recognizer = ActivityRecognizer(
    yolo_model=settings.YOLO_MODEL,
    activity_model_path=settings.ACTIVITY_MODEL,
)