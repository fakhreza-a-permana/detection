from django.contrib import admin
from .models import VideoProcess, DetectionResult

# Register your models here.

@admin.register(VideoProcess)
class VideoProcessAdmin(admin.ModelAdmin):
    list_display = ('filename', 'nama_praktikum', 'status', 'progress', 'waktu_mulai', 'waktu_selesai')
    list_filter = ('status',)
    search_fields = ('filename', 'nama_praktikum')

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('video_id','video', 'frame_number', 'person_id', 'activity', 'confidence')
    list_filter = ('activity', 'person_id')
    search_fields = ('video__filename', 'activity')
