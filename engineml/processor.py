import os,subprocess
import cv2

from django.conf import settings

from web.models import VideoProcess, DetectionResult
from engineml.recognizer_instance import recognizer


class VideoProcessor:
    def __init__(self, job_id, type=None):
        self.job = VideoProcess.objects.get(pk=job_id)

    def process(self):

        try:
            self.job.status = "PROCESSING"
            self.job.save(update_fields=["status"])

            cap = cv2.VideoCapture(self.job.video.path)

            if not cap.isOpened():
                raise Exception("Video tidak dapat dibuka.")

            total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            self.job.frame_total = total_frame
            self.job.save(update_fields=["frame_total"])

            output_dir = os.path.join(settings.MEDIA_ROOT, "output")
            os.makedirs(output_dir, exist_ok=True)

            output_dir_tmp= os.path.join(settings.BASE_DIR,"tmp")
            os.makedirs(output_dir_tmp, exist_ok=True)

            preview_dir = os.path.join(settings.MEDIA_ROOT, "preview")
            os.makedirs(preview_dir, exist_ok=True)

            output_tmp = os.path.join(
                output_dir_tmp,
                f"{self.job.id}.mp4"
            )

            output_path = os.path.join(
                output_dir,
                f"{self.job.id}.mp4"
            )

            preview_path = os.path.join(
                preview_dir,
                f"{self.job.id}.jpg"
            )

            writer = cv2.VideoWriter(
                output_tmp,
                cv2.VideoWriter_fourcc(*'mp4v'),
                fps,
                (width, height)
            )

            frame_number = 0

            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                frame_number += 1

                result = recognizer.detect(frame)
                for det in result["detections"]:
                    DetectionResult.objects.create(
                        video=self.job,
                        frame_number=frame_number,
                        person_id=det["person"],
                        activity=det["activity"],
                        confidence=det["activity_confidence"]
                    )

                annotated = result["frame"]

                writer.write(annotated)

                # Simpan preview setiap 10 frame
                if frame_number % 10 == 0:
                    cv2.imwrite(preview_path, annotated)

                progress = int(
                    frame_number * 100 / total_frame
                )

                self.job.progress = progress
                self.job.frame_current = frame_number
                self.job.person_count = result["person_count"]

                self.job.save(update_fields=[
                    "progress",
                    "frame_current",
                    "person_count"
                ])

            cap.release()
            writer.release()

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", output_tmp,
                "-vf", "scale=960:-2",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "27",
                "-pix_fmt", "yuv420p",
                output_path
            ], check=True)

            os.remove(output_tmp)
            self.job.progress = 100
            self.job.status = "COMPLETED"

            self.job.output_video.name = f"output/{self.job.id}.mp4"

            self.job.save()

        except Exception as e:

            self.job.status = "FAILED"
            self.job.error_message = str(e)

            self.job.save(update_fields=[
                "status",
                "error_message"
            ])

            raise