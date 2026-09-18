# AI-Powered Video Dubbing Platform 🎥🤖

A lightweight video dubbing and translation pipeline built with **Python**, **FastAPI**, and **FFmpeg**. This platform automatically extracts audio from videos, transcribes speech, translates text into target languages, synthesizes localized voiceovers, and generates synchronized, chunked subtitles. **Designed for seamless local development and ready to be deployed to production with proper infrastructure using Docker and Docker Compose.**

---

## ✨ Features

* **⚡ Lightning-Fast STT:** Powered by **Groq Whisper** (`whisper-large-v3-turbo`) for near-instant speech-to-text transcription.
* **🌐 Smart Translation:** Integrates with **Hugging Face Llama** serverless inference routers for accurate multi-language translation.
* **🗣️ Localized Voice Synthesis:** Uses `gTTS` to generate natural speech audio mapped to target languages (Spanish, French, German, etc.).
* **🎬 Robust FFmpeg Integration:** Features an automatic path-resolver that detects FFmpeg and FFprobe across system PATH, standard directories, and Windows WinGet package folders (`*Gyan.FFmpeg*`).
* **📝 Synchronized Subtitles:** Includes a custom sentence-based chunking algorithm that generates clean `.srt` files, preventing text overflow on screen.
* **🐳 Production & Local Ready:** Fully containerized with a custom `Dockerfile` and `docker-compose.yml` for effortless deployment across any environment.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, Uvicorn, SQLAlchemy, Pydantic v2
* **AI / ML Providers:** Groq API (Whisper), Hugging Face Hub (Llama), gTTS (Google Text-to-Speech)
* **Media Processing:** FFmpeg / FFprobe
* **Containerization:** Docker, Docker Compose
* **Database:** SQLite (`dubbing.db`)

---

## 📂 Project Structure

```text
├── app/
│   ├── api/               # FastAPI routers and endpoints
│   ├── core/              # Configuration and logging settings
│   ├── models/            # SQLAlchemy database models
│   ├── services/          # Business logic & AI providers
│   │   ├── ai/            # STT, Translation, and TTS providers
│   │   └── pipeline.py    # Core dubbing & FFmpeg orchestration pipeline
│   └── main.py            # FastAPI application entrypoint
├── storage/               # Local uploads and generated output artifacts
├── Dockerfile             # Container configuration file
├── docker-compose.yml     # Multi-container orchestration setup
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
└── demo_runner.py         # Script for programmatic API testing