from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Core functionality endpoints
    path('fetch-news/', views.fetch_news_view, name='fetch-news'),
    path('show-news/', views.get_all_news, name='show-news'),
    path('show-news-script/', views.get_all_news_script, name='show-news-script'),
    path('ask-gemini/', views.ask_gemini, name='ask-gemini'),
    path('tts/<int:news_id>/', views.tts_news_by_id, name='tts-news'),
    path('avatar/<int:news_id>/', views.generate_avatar_video, name='avatar-video'),

    # Utility and monitoring endpoints
    path('check-ffmpeg/', views.check_ffmpeg, name='check-ffmpeg'),
    path('video-status/<int:news_id>/', views.get_video_status, name='video-status'),

    path('check-video/<int:news_id>/', views.check_video_exists, name='check_video_exists'),
    path('news_videos/<str:filename>', views.serve_video, name='serve_video'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)