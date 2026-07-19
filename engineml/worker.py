import threading
from engineml.processor import VideoProcessor

def start(job):

    thread = threading.Thread(
        target=VideoProcessor(job).process,
        daemon=True
    )

    thread.start()

def restart(job):

    thread = threading.Thread(
        target=VideoProcessor(job).process,
        daemon=True
    )

    thread.start()