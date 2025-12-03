import subprocess
import json
import os
from gtts import gTTS


# ✅ Step 1: Extract audio from MP4
def extract_audio(video_path, audio_path):
    """
    Extracts audio from input video (mp4) and saves as WAV.
    """
    command = [
        "ffmpeg",
        "-y",                # overwrite output
        "-i", video_path,    # input video
        "-vn",               # no video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",          # sample rate
        "-ac", "1",              # mono
        audio_path
    ]
    print("🎬 Extracting audio from video...")
    subprocess.run(command, check=True)
    return audio_path


# ✅ Step 2: Transcribe audio with Whisper CLI
def transcribe_with_whisper(audio_path, transcript_json):
    """
    Transcribes audio into text using OpenAI Whisper CLI.
    Saves transcript as JSON.
    """
    command = [
        "whisper", audio_path,
        "--model", "base",
        "--output_format", "json",
        "--output_dir", os.path.dirname(transcript_json)
    ]
    print("🗣️ Running Whisper transcription...")
    subprocess.run(command, check=True)

    # Move Whisper output to expected path
    default_json = os.path.join(
        os.path.dirname(transcript_json),
        os.path.splitext(os.path.basename(audio_path))[0] + ".json"
    )
    if os.path.exists(default_json):
        os.rename(default_json, transcript_json)

    return transcript_json


# ✅ Step 3: Align transcript (stub)
def align_with_whisperx(audio_path, transcript_json):
    """
    Dummy alignment function.
    In real WhisperX usage, you'd run a proper aligner.
    """
    with open(transcript_json, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    segments = []
    for i, seg in enumerate(transcript.get("segments", [])):
        segments.append({
            "id": i,
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": seg.get("text", "")
        })

    print(f"🧩 Alignment complete — {len(segments)} segments found.")
    return segments


# ✅ Step 4: Generate dubbed audio (TTS)
def create_dubbed_audio(aligned_segments, dubbed_audio_path, target_lang="en"):
    """
    Generate dubbed audio track using Google Text-to-Speech (gTTS).
    Replace with a more advanced TTS engine for production.
    """
    # Map web form languages to gTTS codes
    lang_map = {
        "hi": "hi",  # Hindi
        "te": "te",  # Telugu
        "kn": "kn",  # Kannada
        "ta": "ta",  # Tamil (optional)
        "en": "en"   # English fallback
    }

    lang_code = lang_map.get(target_lang, "en")

    # Combine text segments into one full string
    text = " ".join([seg["text"] for seg in aligned_segments]).strip()

    if not text:
        raise ValueError("No text found in aligned segments to generate TTS.")

    print(f"🗣️ Generating TTS in language '{lang_code}'...")

    # Generate and save speech
    tts = gTTS(text=text, lang=lang_code)
    tts.save(dubbed_audio_path)

    print(f"🎧 Dubbed audio created at: {dubbed_audio_path}")
    return dubbed_audio_path


# ✅ Step 5: Replace audio track in MP4
def replace_audio_in_video(video_path, dubbed_audio_path, output_path):
    """
    Replace original video’s audio track with dubbed audio using proper encoding.
    Ensures sound is audible and compatible.
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,            # original video
        "-i", dubbed_audio_path,     # dubbed audio
        "-c:v", "copy",              # copy video stream
        "-c:a", "aac",               # re-encode audio as AAC
        "-b:a", "192k",              # set audio bitrate
        "-map", "0:v:0",             # video from first input
        "-map", "1:a:0",             # audio from second input
        "-shortest",                 # cut to shortest stream
        output_path
    ]
    print("🎞️ Merging dubbed audio with video (FFmpeg)...")
    subprocess.run(command, check=True)
    print(f"✅ Video created with sound at: {output_path}")
    return output_path


# ✅ Step 6: Full pipeline (used by app.py)
def process_video(video_path, output_dir, target_lang="en"):
    """
    Full pipeline: extract audio, transcribe, generate dubbed audio, and replace in video.
    Returns path to final output video.
    """
    audio_path = os.path.join(output_dir, "audio.wav")
    transcript_json = os.path.join(output_dir, "transcript.json")
    dubbed_audio_path = os.path.join(output_dir, "dubbed_audio.mp3")
    output_video_path = os.path.join(output_dir, "output.mp4")

    print("🎬 Step 1: Extracting audio...")
    extract_audio(video_path, audio_path)

    print("🗣️ Step 2: Transcribing audio with Whisper...")
    transcribe_with_whisper(audio_path, transcript_json)

    print("⏱️ Step 3: Aligning transcript...")
    aligned_segments = align_with_whisperx(audio_path, transcript_json)

    print(f"🎧 Step 4: Creating dubbed audio in '{target_lang}'...")
    create_dubbed_audio(aligned_segments, dubbed_audio_path, target_lang)

    print("🎞️ Step 5: Replacing original audio with dubbed track...")
    replace_audio_in_video(video_path, dubbed_audio_path, output_video_path)

    print("✅ Video dubbing complete:", output_video_path)
    return output_video_path
