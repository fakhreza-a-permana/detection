from django.db import models

# Create your models here.

class VideoProcess(models.Model):

    STATUS_CHOICES = [
        ("QUEUED","Queued"),
        ("PROCESSING","Processing"),
        ("COMPLETED","Completed"),
        ("FAILED","Failed"),
    ]
    nama_praktikum = models.CharField(max_length=255, null=True, blank=True)
    waktu_mulai = models.DateTimeField(null=True, blank=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    filename = models.CharField(max_length=255)
    video = models.FileField(upload_to="uploads/")
    fps= models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="QUEUED")
    progress = models.IntegerField(default=0)
    frame_current = models.IntegerField(default=0)
    frame_total = models.IntegerField(default=0)
    person_count = models.IntegerField(default=0)
    output_video = models.FileField(upload_to="outputs/", null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Video Process"
        verbose_name_plural = "Video Processes"

    def __str__(self):
        return '{} {}'.format(self.filename, self.status)
    
    @property
    def can_restart(self):
        return self.status in ["COMPLETED","FAILED"]

class DetectionResult(models.Model):

    video = models.ForeignKey(
        VideoProcess,
        on_delete=models.CASCADE,
        related_name="detections"
    )
    frame_number = models.IntegerField()
    person_id = models.IntegerField()
    activity = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Detection Result"
        verbose_name_plural = "Detection Results"

    