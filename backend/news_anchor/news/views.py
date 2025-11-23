# views.py (updated)
import logging
import os
import traceback
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.static import serve
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Models / serializers / utils / ai helper
from .models import NewsArticle, AnchoringScript
from .serializers import NewsArticleSerializer, AnchoringScriptSerializer
from .utils import update_news
from .ai_helper import get_ai_response

logger = logging.getLogger(__name__)
# Ensure logger has a handler when running stand-alone for debugging
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Audio/video folders (use BASE_DIR)
BASE_DIR = Path(settings.BASE_DIR)
AUDIO_DIR = BASE_DIR / "news_audios"
VIDEO_DIR = BASE_DIR / "news_videos"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------
# 1) NEWS FETCH / LIST VIEWS
# ---------------------------
def fetch_news_view(request):
    """
    Fetch and update news from API and store in DB.
    Optional query: ?category=technology
    """
    try:
        category = request.GET.get("category")
        update_news(category)
        return JsonResponse({"message": "News fetched and stored successfully!"})
    except Exception as e:
        logger.exception("fetch_news_view failed")
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_all_news(request):
    """
    Get all stored news. Optional query param: ?category=technology
    """
    try:
        category = request.GET.get('category')
        if category:
            news_qs = NewsArticle.objects.filter(category=category).order_by('-published_at')
        else:
            news_qs = NewsArticle.objects.all().order_by('-published_at')

        serializer = NewsArticleSerializer(news_qs, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.exception("get_all_news failed")
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def get_all_news_script(request):
    """
    Get all anchoring scripts. Optional query param: ?category=technology
    """
    try:
        category = request.GET.get('category')
        if category:
            scripts = AnchoringScript.objects.filter(news__category=category).order_by('id')
        else:
            scripts = AnchoringScript.objects.all().order_by('id')

        serializer = AnchoringScriptSerializer(scripts, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.exception("get_all_news_script failed")
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# 2) SCRIPT GENERATION HELPERS
# ---------------------------
def get_existing_script_for_article(article: NewsArticle) -> Optional[AnchoringScript]:
    """
    Safely returns the AnchoringScript object associated with an article, if present.
    Works whether AnchoringScript uses OneToOneField (related_name='script') or FK.
    """
    # Try attribute access (common if OneToOneField with related_name='script')
    try:
        script_obj = getattr(article, "script", None)
        if script_obj:
            return script_obj
    except Exception:
        # attribute may raise if no relation; ignore and try query
        pass

    # Fallback: query AnchoringScript table
    return AnchoringScript.objects.filter(news=article).first()


def generate_or_get_script(article: NewsArticle) -> Tuple[Optional[AnchoringScript], bool]:
    """
    Generate a script only if it doesn't exist. Returns (script_obj, created_flag).
    created_flag == True means a new script was created.
    """
    try:
        existing = get_existing_script_for_article(article)
        if existing:
            return existing, False

        prompt = (
            f"Write a professional TV news anchoring script for this article:\n\n"
            f"Title: {article.title}\n"
            f"Description: {article.description}\n\n"
            f"Keep it natural, engaging, and ready to speak without any labels or directions. "
            f"Make it approximately 100–120 words suitable for 20–25 seconds of speech."
        )

        script_text = get_ai_response(prompt)
        if not script_text:
            logger.warning("AI returned empty script for article id=%s", article.id)
            return None, False

        new_script = AnchoringScript.objects.create(news=article, script=script_text)
        return new_script, True

    except Exception as e:
        logger.exception("generate_or_get_script failed for article id=%s", getattr(article, "id", None))
        return None, False


@api_view(['POST', 'GET'])
def ask_gemini(request):
    """
    Generate anchoring scripts for all or specific news articles using the AI helper.
    Only generates scripts that don't already exist.
    Query or POST body param: news_id (optional)
    """
    try:
        news_id = request.GET.get("news_id") or (request.data.get("news_id") if hasattr(request, "data") else None)
        if news_id:
            articles = NewsArticle.objects.filter(id=news_id)
            if not articles.exists():
                return JsonResponse({"error": f"No news article found with ID {news_id}"}, status=404)
        else:
            articles = NewsArticle.objects.all()

        created_count = skipped_count = failed_count = 0
        total = articles.count()

        for article in articles:
            script_obj, created = generate_or_get_script(article)
            if script_obj:
                if created:
                    created_count += 1
                    logger.info("Generated script for article id=%s title=%s", article.id, article.title)
                else:
                    skipped_count += 1
            else:
                failed_count += 1
                logger.warning("Failed to generate script for article id=%s", article.id)

        return JsonResponse({
            "message": "Script generation completed.",
            "details": {
                "created": created_count,
                "skipped": skipped_count,
                "failed": failed_count,
                "total_processed": total
            }
        })
    except Exception as e:
        logger.exception("ask_gemini failed")
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# 3) TTS HELPERS
# ---------------------------
def ensure_a4f_client():
    """
    Lazily import and return an A4F client instance.
    This avoids import-time failure if the package isn't available.
    """
    try:
        from a4f_local import A4F
        return A4F()
    except Exception as e:
        logger.exception("A4F import/instantiation failed")
        raise


def tts_generate_for_article(news_id: int) -> Tuple[Optional[Path], Optional[str]]:
    """
    Generate (or reuse existing) TTS MP3 for the article's anchoring script.
    Returns (audio_path (Path) or None, error_message or None).
    """
    try:
        article = NewsArticle.objects.filter(id=news_id).first()
        if not article:
            return None, f"No news article found with ID {news_id}"

        script_obj = get_existing_script_for_article(article)
        if not script_obj:
            return None, f"No anchoring script found for news ID {news_id}"

        text = script_obj.script.strip() if script_obj.script else ""
        if not text:
            return None, "Script text is empty"

        safe_filename = AUDIO_DIR / f"script_{news_id}.mp3"

        # If exists, return it (re-use)
        if safe_filename.exists():
            logger.info("Using existing audio file for news_id %s", news_id)
            return safe_filename, None

        # Generate audio (lazy client creation)
        client = ensure_a4f_client()
        # Some providers may require bytes; our client returns bytes
        logger.info("Generating TTS for news_id %s ...", news_id)
        audio_bytes = client.audio.speech.create(
            model="tts-1",
            input=text[:4000],  # be cautious of max token/char limits
            voice="alloy",
            speed=1.0
        )

        if not audio_bytes:
            return None, "TTS provider returned empty audio"

        # Write bytes to file
        with open(safe_filename, "wb") as f:
            f.write(audio_bytes)
        logger.info("TTS saved: %s", safe_filename)
        return safe_filename, None

    except Exception as e:
        logger.exception("tts_generate_for_article failed for news_id=%s", news_id)
        return None, str(e)


@api_view(['GET'])
def tts_news_by_id(request, news_id):
    """
    API endpoint: Convert anchoring script to speech (MP3) by ID and return as attachment.
    """
    try:
        audio_path, error = tts_generate_for_article(int(news_id))
        if error:
            return JsonResponse({"error": error}, status=404)
        # Return file as attachment
        with open(audio_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = f'attachment; filename="{audio_path.name}"'
            return response
    except Exception as e:
        logger.exception("tts_news_by_id failed for news_id=%s", news_id)
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# 4) FFmpeg / MEDIA UTILITIES
# ---------------------------
def get_audio_duration(audio_path: str) -> float:
    """Get audio duration using ffprobe"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ], capture_output=True, text=True, timeout=30)
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning("Could not get audio duration for %s: %s", audio_path, e)
        return 0.0


def verify_video_has_audio(video_path: str) -> bool:
    """Return True if ffprobe finds an audio stream."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
             '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path],
            capture_output=True, text=True, timeout=20
        )
        return 'audio' in (result.stdout or "")
    except Exception as e:
        logger.warning("verify_video_has_audio failed for %s: %s", video_path, e)
        return False


def merge_audio_with_video_fixed(video_path: str, audio_path: str, merged_output_path: str) -> Optional[str]:
    """FFmpeg-based merge ensuring timing / shortest track trimming."""
    try:
        if not os.path.exists(video_path) or not os.path.exists(audio_path):
            logger.error("Missing video or audio for merge: %s %s", video_path, audio_path)
            return None

        # get durations
        video_duration = get_audio_duration(video_path)
        audio_duration = get_audio_duration(audio_path)
        shortest_duration = min(video_duration if video_duration > 0 else float('inf'),
                                audio_duration if audio_duration > 0 else float('inf'))
        if shortest_duration == float('inf'):
            shortest_duration = None  # let ffmpeg handle it

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
        ]
        if shortest_duration:
            cmd += ["-t", str(shortest_duration)]
        cmd += [
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-avoid_negative_ts", "make_zero",
            merged_output_path
        ]
        logger.info("Merging audio+video (fixed): %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0 and os.path.exists(merged_output_path):
            return merged_output_path
        else:
            logger.error("Merge failed: %s", result.stderr)
            return None
    except Exception as e:
        logger.exception("merge_audio_with_video_fixed failed")
        return None


def merge_audio_with_video(video_path: str, audio_path: str, output_path: str) -> bool:
    """Simpler merge that copies video stream and re-encodes audio."""
    try:
        if not os.path.exists(video_path) or not os.path.exists(audio_path):
            logger.error("Missing video/audio for alternative merge")
            return False
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
        logger.info("Alternative merge: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        logger.error("Alternative merge failed: %s", result.stderr)
        return False
    except Exception as e:
        logger.exception("merge_audio_with_video error")
        return False


# ---------------------------
# 5) AVATAR / VIDEO GENERATION
# ---------------------------
# Try to import avatar generation module at runtime; if not present mark unavailable.
try:
    # adjust path if your module is stored outside Python path
    AVATAR_MODULE_PATH = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop",
                                      "personalized-news-anchor", "ai_models", "AI-Commentator-Avatar", "modules")
    if AVATAR_MODULE_PATH not in os.sys.path:
        os.sys.path.append(AVATAR_MODULE_PATH)
    from avatar_generation import generate_lip_synced_video, generate_lip_synced_video_simple  # type: ignore
    AVATAR_GENERATION_AVAILABLE = True
    logger.info("Avatar generation module loaded")
except Exception as e:
    logger.warning("Avatar generation module not available: %s", e)
    AVATAR_GENERATION_AVAILABLE = False

    def generate_lip_synced_video(*args, **kwargs):
        return None

    def generate_lip_synced_video_simple(*args, **kwargs):
        return None


@api_view(['POST', 'GET'])
def generate_avatar_video(request, news_id):
    """
    Full automatic pipeline: ensure script -> TTS -> avatar lip-synced video -> verify/merge audio if needed.
    Returns metadata and a public URL (assuming media is served from /news_videos/).
    """
    start_time = time.time()
    tracker = {"steps": {}, "current_step": None}

    def start_step(name):
        tracker["current_step"] = name
        tracker["steps"][name] = {"start_time": time.time()}
        logger.info("STEP STARTED: %s", name)

    def end_step(name, success=True, info=None):
        if name in tracker["steps"]:
            duration = time.time() - tracker["steps"][name]["start_time"]
            status = "SUCCESS" if success else "FAILED"
            logger.info("%s STEP %s (%.2fs) %s", "✅" if success else "❌", name, duration, f"- {info}" if info else "")

    try:
        start_step("Initial Setup")
        article = NewsArticle.objects.filter(id=news_id).first()
        if not article:
            end_step("Initial Setup", False, f"No article id={news_id}")
            return JsonResponse({"error": f"No article found with ID {news_id}"}, status=404)
        end_step("Initial Setup", True, f"Processing: {article.title}")

        # Script generation / retrieval
        start_step("Script Generation")
        script_obj, created = generate_or_get_script(article)
        if not script_obj:
            end_step("Script Generation", False, "Script generation failed")
            return JsonResponse({"error": "Script generation failed"}, status=500)
        end_step("Script Generation", True, f"{'Created' if created else 'Existing'} script")

        # Audio generation (use helper)
        start_step("Audio Generation")
        audio_path, audio_err = tts_generate_for_article(int(news_id))
        if audio_err:
            end_step("Audio Generation", False, audio_err)
            return JsonResponse({"error": f"Audio generation failed: {audio_err}"}, status=500)
        end_step("Audio Generation", True, f"Audio at {audio_path}")

        # Check avatar module
        start_step("Module Check")
        if not AVATAR_GENERATION_AVAILABLE:
            end_step("Module Check", False, "Avatar generation module missing")
            return JsonResponse({"error": "Avatar generation module not available"}, status=500)
        end_step("Module Check", True, "Avatar module ready")

        # Prepare output path and call avatar generator (primary then simplified)
        start_step("Video Generation")
        output_path = VIDEO_DIR / f"{news_id}.mp4"
        output_path_parent = output_path.parent
        output_path_parent.mkdir(parents=True, exist_ok=True)

        # Call generator
        result_video = generate_lip_synced_video(
            audio_path=str(audio_path),
            face_path=None,
            output_path=str(output_path),
            news_id=news_id
        )

        if not result_video or not os.path.exists(result_video):
            logger.warning("Primary avatar generation failed, trying simplified method")
            result_video = generate_lip_synced_video_simple(
                audio_path=str(audio_path),
                face_path=None,
                output_path=str(output_path),
                news_id=news_id
            )

        if not result_video or not os.path.exists(result_video):
            end_step("Video Generation", False, "No output produced by avatar generators")
            return JsonResponse({"error": "Video generation failed - no output created"}, status=500)
        end_step("Video Generation", True, f"Video created: {result_video}")

        # Verify audio, attempt emergency merge if missing
        start_step("Audio Verification")
        final_has_audio = verify_video_has_audio(str(output_path))
        if not final_has_audio:
            logger.warning("Generated video missing audio; attempting emergency merge")
            emergency_output = output_path.with_suffix(".emergency.mp4")
            emergency_merged = False

            for i, merge_func in enumerate([merge_audio_with_video_fixed, merge_audio_with_video], start=1):
                logger.info("Trying merge method %d", i)
                try:
                    merged = merge_func(str(output_path), str(audio_path), str(emergency_output))
                    if merged and os.path.exists(emergency_output):
                        # Replace original with merged file
                        os.replace(emergency_output, output_path)
                        emergency_merged = True
                        logger.info("Emergency merge succeeded with method %d", i)
                        break
                except Exception as e:
                    logger.exception("Merge method %d raised exception", i)
                    continue

            if emergency_merged:
                final_has_audio = verify_video_has_audio(str(output_path))
                end_step("Audio Verification", True, "Audio restored by emergency merge")
            else:
                end_step("Audio Verification", False, "Audio not restored after merges")
                # Continue but mark as missing
        else:
            end_step("Audio Verification", True, "Audio present in generated video")

        # Final validation and metadata
        start_step("Final Validation")
        if not os.path.exists(output_path):
            end_step("Final Validation", False, "Final file missing")
            return JsonResponse({"error": "Final output file not found"}, status=500)

        file_size = os.path.getsize(output_path) / (1024 * 1024)
        final_duration = 0.0
        if final_has_audio:
            try:
                final_duration = get_audio_duration(str(output_path))
            except Exception:
                final_duration = get_audio_duration(str(audio_path)) or 0.0

        end_step("Final Validation", True,
                 f"Size: {file_size:.1f}MB Duration: {final_duration:.2f}s Audio: {final_has_audio}")

        elapsed = time.time() - start_time
        # Return absolute URL if request has build_absolute_uri available
        try:
            video_url = request.build_absolute_uri(f"/news_videos/{news_id}.mp4")
        except Exception:
            video_url = f"/news_videos/{news_id}.mp4"

        response_data = {
            "status": "success",
            "news_id": str(news_id),
            "video_url": video_url,
            "execution_time": f"{elapsed:.2f}s",
            "has_audio": bool(final_has_audio),
            "video_path": str(output_path),
            "file_size_mb": round(file_size, 2),
            "duration_seconds": round(final_duration, 2),
            "title": article.title
        }

        logger.info("AVATAR GENERATION COMPLETED for %s", news_id)
        return JsonResponse(response_data)

    except Exception as e:
        logger.exception("generate_avatar_video failed")
        # Report current step if available
        cur = tracker.get("current_step")
        if cur:
            logger.error("Failed during step: %s", cur)
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------
# 6) FFmpeg HEALTH CHECK & VIDEO STATUS
# ---------------------------
@api_view(['GET'])
def check_ffmpeg(request):
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        available = result.returncode == 0
        version_line = result.stdout.splitlines()[0] if result.stdout else "Unknown"
        return JsonResponse({"available": available, "version": version_line})
    except Exception:
        return JsonResponse({"available": False, "version": None})


@api_view(['GET'])
def get_video_status(request, news_id):
    """Check if video exists and whether it has audio; returns metadata."""
    try:
        video_path = VIDEO_DIR / f"{news_id}.mp4"
        if not video_path.exists():
            return JsonResponse({"exists": False})
        has_audio = verify_video_has_audio(str(video_path))
        size_mb = video_path.stat().st_size / (1024 * 1024)
        duration = get_audio_duration(str(video_path)) if has_audio else 0.0
        return JsonResponse({
            "exists": True,
            "has_audio": has_audio,
            "size_mb": round(size_mb, 2),
            "duration_seconds": round(duration, 2),
            "path": str(video_path)
        })
    except Exception as e:
        logger.exception("get_video_status failed")
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
def check_video_exists(request, news_id):
    """
    Simple helper to check for video file on disk.
    """
    try:
        filename = f"{news_id}.mp4"
        video_path = VIDEO_DIR / filename
        exists = video_path.exists()
        return JsonResponse({
            'exists': exists,
            'video_url': f'/news_videos/{filename}' if exists else None,
            'file_path': str(video_path)
        })
    except Exception as e:
        logger.exception("check_video_exists failed")
        return JsonResponse({'exists': False, 'error': str(e)}, status=500)


# Serve video (if you want Django to serve files in dev)
def serve_video(request, filename):
    try:
        video_path = VIDEO_DIR / filename
        if video_path.exists():
            return serve(request, filename, document_root=str(VIDEO_DIR))
        return JsonResponse({'error': 'Video not found'}, status=404)
    except Exception as e:
        logger.exception("serve_video failed")
        return JsonResponse({'error': str(e)}, status=500)
