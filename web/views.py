from django.shortcuts import render
from web.models import VideoProcess
from django.shortcuts import render, redirect
from engineml.worker import start

# Create your views here.
def index(request):
    video_processes = VideoProcess.objects.all()
    return render(request, 'input_video.html', {'video_processes': video_processes})


def upload_video(request):
    try:
        if request.method == 'POST':
            video = request.FILES['video']
            print(video)
            video_process = VideoProcess.objects.create(
                filename = video.name,
                video = video,
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
    return render(request, 'detail_video.html', {'video_process': video_process})


def restart_process(request, id):
    video_process = VideoProcess.objects.get(id=id)
    video_process.status = "QUEUED"
    video_process.save()

    start(video_process.id)
    return redirect('index')