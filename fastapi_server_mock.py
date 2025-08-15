from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import time
import os
import mimetypes
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock TTS API", description="Mock Text-to-Speech API for testing", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice_id: str = "en-US-sarah"  # Default voice
    speed: int = 100  # Default speed (100 = normal)

class TTSResponse(BaseModel):
    audio_url: str
    status: str
    message: str

class AudioUploadResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "Mock TTS API Server is running"}

@app.post("/generate-tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    """
    Mock TTS generation - returns a sample audio file URL for testing
    """
    # Simulate processing time
    time.sleep(1)
    
    # For demo purposes, return a sample audio URL
    # In production, this would be the actual generated audio URL from Murf
    mock_audio_urls = {
        "en-US-sarah": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "en-US-john": "https://www.soundjay.com/misc/sounds/bell-ringing-04.wav", 
        "en-GB-emma": "https://www.soundjay.com/misc/sounds/bell-ringing-03.wav"
    }
    
    # Use a more reliable test audio URL
    audio_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    
    # Try to use a better test URL that actually works
    test_urls = [
        "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
        "https://file-examples.com/storage/fe68c1c6b3ad836ec6a5a4d/2017/11/file_example_MP3_700KB.mp3",
        "https://sample-videos.com/zip/10/mp3/SampleAudio_0.4mb_mp3.mp3"
    ]
    
    return TTSResponse(
        audio_url=test_urls[0],  # Use first URL as default
        status="success",
        message=f"Mock TTS generated successfully for voice '{request.voice_id}' at {request.speed}% speed. Text: '{request.text[:50]}...'"
    )

@app.post("/upload-audio", response_model=AudioUploadResponse)
async def upload_audio(audio_file: UploadFile = File(...)):
    """
    Mock audio file upload - simulates uploading to server for testing
    """
    try:
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        original_filename = audio_file.filename or "audio"
        name, ext = os.path.splitext(original_filename)
        
        # If no extension, try to determine from content type
        if not ext and audio_file.content_type:
            ext = mimetypes.guess_extension(audio_file.content_type) or ".webm"
        
        filename = f"{name}_{timestamp}{ext}"
        file_path = uploads_dir / filename
        
        # Read and save the file
        contents = await audio_file.read()
        file_size = len(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Simulate some processing time
        time.sleep(0.5)
        
        return AudioUploadResponse(
            filename=filename,
            content_type=audio_file.content_type,
            size=file_size,
            status="success",
            message=f"Mock upload successful! File saved as {filename}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload audio file: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Mock TTS API"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Mock TTS Server for testing...")
    print("This server returns mock audio URLs for testing the UI")
    print("Replace with real fastapi_server.py when you have a Murf API key")
    uvicorn.run(app, host="127.0.0.1", port=8000)
