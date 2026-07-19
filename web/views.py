import cv2

from django.db.models import Count
from django.shortcuts import render
from web.models import VideoProcess,DetectionResult
from django.shortcuts import render, redirect
from engineml.worker import start
from django.conf import settings

# Create your views here.
def index(request):
    video_processes = VideoProcess.objects.all().order_by('-waktu_mulai')
    return render(request, 'input_video.html', {'video_processes': video_processes})


def upload_video(request):
    try:
        if request.method == 'POST':
            video = request.FILES['video']
            print(video)
            video_process = VideoProcess.objects.create(
                filename = video.name,
                video = video,
                nama_praktikum = request.POST['name'],
                waktu_mulai = request.POST['start_time'],
                waktu_selesai = request.POST['end_time'],
            )
            start(video_process.id)
            return redirect('index')
        else:
            return render(request, 'input_video.html')
    except Exception as e:
        print(e)
        return render(request, 'input_video.html', {'error': str(e)})


def detail_video(request, id):
    video_process = VideoProcess.objects.get(id=id)
    vid_path = settings.BASE_DIR / "media" / f"{video_process.video}"
    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    statistics = (
        DetectionResult.objects
        .filter(video=video_process)
        .values("activity")
        .annotate(frame_count=Count("frame_number", distinct=True))
    )

    summary = []

    for row in statistics:

        duration = row["frame_count"] / fps if fps else 0

        summary.append({
            "activity": row["activity"],
            "frame_count": row["frame_count"],
            "duration": round(duration, 2),
        })

    return render(request, 'detail_video.html', {'video_process': video_process, 'summary': summary})


def restart_process(request, id):
    video_process = VideoProcess.objects.get(id=id)
    detail= DetectionResult.objects.filter(video=video_process)
    print(detail.count())
    video_process.status = "QUEUED"
    
    video_process.save()
    detail.delete()
    start(video_process.id)
    return redirect('index')