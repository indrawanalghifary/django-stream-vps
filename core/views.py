from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from . import models, forms, services
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
# Create your views here.

def login_view(request):
    return render(request, 'core/login.html')

@login_required
def home(request):
    lives = models.liveModel.objects.all()
    return render(request, 'core/home.html', {'lives': lives})

@login_required
def create_live(request):
    media_files = models.mediaFileModel.objects.all()
    presets = models.configFFMPEGModel.objects.all()
    if request.method == 'POST':
        form = forms.LiveModelForm(request.POST)
        if form.is_valid():
            live = form.save(commit=False)
            live.user = request.user
            live.save()
            messages.success(request, 'Live stream created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = forms.LiveModelForm()
    return render(request, 'core/create_live.html', {'form': form, 'media_files': media_files, 'presets': presets})

@login_required
def edit_live(request, live_id):
    live = get_object_or_404(models.liveModel, id=live_id)
    media_files = models.mediaFileModel.objects.all()
    presets = models.configFFMPEGModel.objects.all()

    if request.method == 'POST':
        form = forms.LiveModelForm(request.POST, instance=live)
        # Set choices for preset field to ensure all presets are available
        form.fields['preset'].queryset = presets
        if form.is_valid():
            form.save()
            messages.success(request, 'Live stream updated successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = forms.LiveModelForm(instance=live)
        # Set choices for preset field to ensure all presets are available
        form.fields['preset'].queryset = presets
    return render(request, 'core/edit_live.html', {'form': form, 'live': live, 'media_files': media_files, 'presets': presets})

@login_required
def delete_live(request, live_id):
    live = get_object_or_404(models.liveModel, id=live_id)
    if request.method == 'POST':
        live.delete()
        messages.success(request, 'Live stream deleted successfully!')
        return redirect('home')
    return render(request, 'core/delete_live_confirm.html', {'live': live})

@login_required
def live_detail(request, live_id):
    live = get_object_or_404(models.liveModel, id=live_id)
    return JsonResponse({
        'id': live.id,
        'title': live.title,
        'description': live.description,
        'file_or_url': live.file_or_url,
        'output_rtmp': live.output_rtmp,
        'preset': live.preset.preset_name if live.preset else None,
        'created_at': live.created_at.isoformat(),
        'updated_at': live.updated_at.isoformat(),
    })

@login_required
def upload_media(request):
    if request.method == 'POST':
        form = forms.MediaFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            media_file = models.mediaFileModel(file=request.FILES['file'])
            media_file.save()
            messages.success(request, 'Media file uploaded successfully!')
            return redirect('upload_success', media_id=media_file.id)
    else:
        form = forms.MediaFileUploadForm()
    return render(request, 'core/upload_media.html', {'form': form})

@login_required
def upload_success(request, media_id):
    media_file = get_object_or_404(models.mediaFileModel, id=media_id)
    return render(request, 'core/upload_success.html', {'media_file': media_file})

@login_required
def start_live_process(request, live_id):
    if request.method == 'POST':
        try:
            live = get_object_or_404(models.liveModel, id=live_id)
            if not live.preset:
                return JsonResponse({'error': 'No preset configured for this live stream'}, status=400)
            pid = services.start_live_stream(live.file_or_url, live.output_rtmp, live.preset.parameters)
            log = models.logsProcessModel(live_model=live, pid=pid, status='running')
            log.save()
            return JsonResponse({'message': 'Live process started', 'pid': pid, 'log_id': log.id, 'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def stop_live_process(request, log_id):
    if request.method == 'POST':
        try:
            log = get_object_or_404(models.logsProcessModel, id=log_id)
            success = services.stop_process(log.pid) or services.is_process_running(log.pid) == False
            if success:
                log.status = 'stopped'
                log.save()
                return JsonResponse({'message': 'Live process stopped', 'status': 'success'})
            else:
                return JsonResponse({'error': 'Failed to stop process', 'status': 'error'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def view_logs(request, live_id):
    live = get_object_or_404(models.liveModel, id=live_id)
    logs = models.logsProcessModel.objects.filter(live_model=live)
    for log in logs:
        stopped = services.is_process_running(log.pid)
        if not stopped and log.status == 'running':
            log.status = 'stopped'
            log.save()
    return JsonResponse({'logs': [{'id': log.id, 'pid': log.pid, 'status': log.status, 'timestamp': log.timestamp.isoformat()} for log in logs]})

@login_required
def configure_ffmpeg(request):
    if request.method == 'POST':
        form = forms.ConfigFFMPEGModelForm(request.POST)
        if form.is_valid():
            config = form.save()
            messages.success(request, 'FFmpeg preset saved successfully!')
            return redirect('config_success', config_id=config.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = forms.ConfigFFMPEGModelForm()
    return render(request, 'core/configure_ffmpeg.html', {'form': form})

@login_required
def config_success(request, config_id):
    config = get_object_or_404(models.configFFMPEGModel, id=config_id)
    return render(request, 'core/config_success.html', {'config': config})

@login_required
def delete_ffmpeg_config(request, config_id):
    config = get_object_or_404(models.configFFMPEGModel, id=config_id)
    if request.method == 'POST':
        config.delete()
        messages.success(request, 'FFmpeg preset deleted successfully!')
        return redirect('list_ffmpeg_configs')
    return render(request, 'core/delete_config_confirm.html', {'config': config})

@login_required
def list_ffmpeg_configs(request):
    configs = models.configFFMPEGModel.objects.all()
    return render(request, 'core/list_ffmpeg_configs.html', {'configs': configs})

@login_required
def view_media_files(request):
    media_files = models.mediaFileModel.objects.all()
    return render(request, 'core/view_media_files.html', {'media_files': media_files})

@login_required
def delete_media_file(request, media_id):
    media_file = get_object_or_404(models.mediaFileModel, id=media_id)
    if request.method == 'POST':
        media_file.file.delete()
        media_file.delete()
        messages.success(request, 'Media file deleted successfully!')
        return redirect('view_media_files')
    return render(request, 'core/delete_media_confirm.html', {'media_file': media_file})

