from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('live/create/', views.create_live, name='create_live'),
    path('live/<int:live_id>/', views.live_detail, name='live_detail'),
    path('live/<int:live_id>/edit/', views.edit_live, name='edit_live'),
    path('live/<int:live_id>/delete/', views.delete_live, name='delete_live'),
    path('upload-media/', views.upload_media, name='upload_media'),
    path('upload-success/<int:media_id>/', views.upload_success, name='upload_success'),
    path('start-live/<int:live_id>/', views.start_live_process, name='start_live_process'),
    path('stop-live/<int:log_id>/', views.stop_live_process, name='stop_live_process'),
    path('logs/<int:live_id>/', views.view_logs, name='view_logs'),
    path('configure-ffmpeg/', views.configure_ffmpeg, name='configure_ffmpeg'),
    path('config-success/<int:config_id>/', views.config_success, name='config_success'),
    path('ffmpeg-config/<int:config_id>/delete/', views.delete_ffmpeg_config, name='delete_ffmpeg_config'),
    path('ffmpeg-configs/', views.list_ffmpeg_configs, name='list_ffmpeg_configs'),
    path('media-files/', views.view_media_files, name='view_media_files'),
    path('media-file/<int:media_id>/delete/', views.delete_media_file, name='delete_media_file'),
]
