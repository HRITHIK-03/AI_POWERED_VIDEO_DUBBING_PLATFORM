import os
import subprocess
import json
import shutil
import glob
from app.database import SessionLocal
from app.models.job import JobModel, JobStatus
from app.services.storage import storage_service
from app.services.ai.stt_provider import OpenAISTTProvider
from app.services.ai.translation_provider import OpenAITranslationProvider
from app.services.ai.tts_provider import TTSProvider
from app.core.logging import logger

def get_ffmpeg_binary(binary_name: str) -> str:
    """Locates ffmpeg or ffprobe across system PATH, WinGet directories, or standard Windows paths."""
    exe_name = f"{binary_name}.exe" if os.name == 'nt' else binary_name
    
    # 1. Check system PATH via shutil.which
    found = shutil.which(binary_name)
    if found:
        return found
        
    # 2. Check WinGet installation paths for Windows users (Gyan.FFmpeg)
    if os.name == 'nt':
        winget_pattern = os.path.expanduser(f"~\\AppData\\Local\\Microsoft\\WinGet\\Packages\\*Gyan.FFmpeg*\\bin\\{exe_name}")
        winget_matches = glob.glob(winget_pattern)
        if winget_matches:
            return winget_matches[0]

    # 3. Check common Windows installation directories
    common_paths = [
        os.path.join(r"C:\ffmpeg\bin", exe_name),
        os.path.join(r"C:\Program Files\FFmpeg\bin", exe_name),
        os.path.join(r"C:\ProgramData\chocolatey\bin", exe_name),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    return binary_name  # Fallback to plain string

def get_video_duration(video_path: str) -> float:
    try:
        ffprobe_exe = get_ffmpeg_binary("ffprobe")
        cmd = [ffprobe_exe, "-v", "quiet", "-print_format", "json", "-show_format", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=(os.name == 'nt' and not os.path.isabs(ffprobe_exe)))
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        logger.warning(f"ffprobe duration extraction failed: {e}. Defaulting to 10.0s")
        return 10.0

def run_dubbing_pipeline(job_id: str):
    db = SessionLocal()
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        db.close()
        return

    try:
        job.status = JobStatus.PROCESSING
        job.progress = 10
        db.commit()

        input_video_path = storage_service.get_upload_path(job.id)
        out_folder = storage_service.create_output_dir(job.id)
        
        audio_path = os.path.join(out_folder, "extracted_audio.wav")
        dubbed_audio_path = os.path.join(out_folder, "dubbed_audio.mp3")
        output_video_path = os.path.join(out_folder, "dubbed_video.mp4")
        transcript_path = os.path.join(out_folder, "transcript.json")
        subtitle_path = os.path.join(out_folder, "subtitles.srt")

        video_duration = get_video_duration(input_video_path)
        ffmpeg_exe = get_ffmpeg_binary("ffmpeg")
        use_shell = (os.name == 'nt' and not os.path.isabs(ffmpeg_exe))

        # 1. Extract audio via FFmpeg
        job.progress = 30
        db.commit()
        subprocess.run([ffmpeg_exe, "-i", input_video_path, "-q:a", "0", "-map", "a", audio_path, "-y"], check=True, shell=use_shell)

        # 2. STT via Groq Whisper
        stt = OpenAISTTProvider()
        transcript_data = stt.transcribe(audio_path)
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f)
        job.progress = 50
        db.commit()

        # 3. Translation via Llama
        translator = OpenAITranslationProvider()
        translated_text = translator.translate(transcript_data["text"], job.target_language)
        job.progress = 70
        db.commit()

        # 4. TTS via gTTS
        tts = TTSProvider()
        dubbed_audio_path = tts.synthesize(translated_text, dubbed_audio_path, job.target_language, duration=video_duration)
        
        # 5. Final Multiplexing (Video + Dubbed Audio)
        subprocess.run([
            ffmpeg_exe, "-i", input_video_path, "-i", dubbed_audio_path,
            "-c:v", "copy", 
            "-c:a", "aac", "-b:a", "192k", 
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", output_video_path, "-y"
        ], check=True, shell=use_shell)

        # 6. Chunked SRT Subtitle generation (Prevents whole-screen text overflow)
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int(int((seconds - int(seconds)) * 1000))
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        sentences = [s.strip() for s in translated_text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        chunk_duration = video_duration / max(len(sentences), 1)

        with open(subtitle_path, "w", encoding="utf-8") as f:
            start_time = 0.0
            for i, sentence in enumerate(sentences, start=1):
                end_time = min(start_time + chunk_duration, video_duration)
                f.write(f"{i}\n")
                f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                f.write(f"{sentence}.\n\n")
                start_time = end_time

        job.output_video_path = output_video_path
        job.transcript_path = transcript_path
        job.subtitle_path = subtitle_path
        job.status = JobStatus.COMPLETED
        job.progress = 100
        db.commit()
        logger.info(f"Job {job_id} successfully completed.")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
    finally:
        db.close()