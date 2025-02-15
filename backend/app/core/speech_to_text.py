"""
Speech to text conversion functionality.
Handles the conversion of audio data to text using various services.
"""

import logging
import asyncio
import tempfile
from app.core.hands.utils import SLInference
# import cv2
from collections import deque

import io
import logging

import httpx
from pydub import AudioSegment
import os

from app.core.configs.config import settings

logger = logging.getLogger(__name__)


async def convert_webm_to_mp3(webm_bytes: bytes) -> bytes:
    """Convert webm audio bytes to mp3 format"""
    try:
        # Create temporary files for conversion
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_tmp, \
             tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_tmp:
            
            # Write webm data to temp file
            webm_tmp.write(webm_bytes)
            webm_tmp.flush()
            
            # Convert webm to mp3 using pydub
            audio = AudioSegment.from_file(webm_tmp.name, format='webm')
            audio.export(mp3_tmp.name, format='mp3')
            
            # Read the converted mp3 data
            with open(mp3_tmp.name, 'rb') as f:
                mp3_bytes = f.read()
            
            # Clean up temp files
            os.unlink(webm_tmp.name)
            os.unlink(mp3_tmp.name)
            
            return mp3_bytes
    except Exception as e:
        logger.error(f"Error converting webm to mp3: {e}")
        raise ValueError("Failed to convert audio format")


async def convert_speech_to_text(voice_bytes: io.BytesIO) -> str:
    # Convert webm to mp3 first
    mp3_bytes = await convert_webm_to_mp3(voice_bytes.getvalue())
    return (await __hf_converter(mp3_bytes)).strip()


async def __hf_converter(voice_bytes: bytes) -> str:
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
    headers = {"Authorization": f"Bearer {settings.HF_TOKEN.get_secret_value()}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=headers, content=voice_bytes)
        json_resp = response.json()
        logger.debug(f"Response from HF: {json_resp}")
        return json_resp["text"]


async def speech_to_text(voice_bytes: bytes) -> str:
    # Convert webm to mp3 first
    mp3_bytes = await convert_webm_to_mp3(voice_bytes)
    return (await __hf_converter(mp3_bytes)).strip()


async def video_to_text(video_bytes: bytes) -> str:
    """
    Convert video to text using an SLInference model.
    This function saves the video bytes to a temporary file, extracts frames via OpenCV,
    feeds them to an inference thread, and aggregates the recognized gestures.

    Args:
        video_bytes: Raw bytes of the video file (e.g., MP4 format).

    Returns:
        The recognized gesture as text (or an empty string if none).
    
    Raises:
        ValueError: If the video data cannot be processed.
    """
    try:
        # Save video bytes to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            tmp_file.write(video_bytes)
            tmp_file.flush()
            tmp_path = tmp_file.name
        logger.info(f"Temporary video file created at {tmp_path}")
        
        # Initialize the SLInference thread; adjust the config path as needed
        inference_thread = SLInference("configs/config.json")
        inference_thread.start()
        
        # Open the temporary video file using OpenCV
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            logger.error("Failed to open video stream from temporary file")
            inference_thread.stop()
            return ""
        
        gestures_deque = deque(maxlen=5)
        frame_count = 0
        
        # Process a fixed number of frames (e.g., 60 frames ~2 seconds at 30 FPS)
        while cap.isOpened() and frame_count < 60:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize the frame to 224x224 as expected by the model
            frame_resized = cv2.resize(frame, (224, 224))
            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Feed the frame into the inference thread
            inference_thread.input_queue.append(frame_rgb)
            
            # Wait to simulate real-time processing (~33ms per frame)
            await asyncio.sleep(1 / 30)
            
            # Get the current prediction from the inference thread (assumes inference_thread.pred is updated)
            gesture = inference_thread.pred
            if gesture and gesture not in ['no', '']:
                if not gestures_deque or (gestures_deque and gesture != gestures_deque[-1]):
                    gestures_deque.append(gesture)
            frame_count += 1
        
        cap.release()
        inference_thread.stop()  # Ensure the inference thread is stopped
        
        recognized_text = gestures_deque[-1] if gestures_deque else ""
        logger.info(f"Recognized gesture: {recognized_text}")
        return recognized_text
    except Exception as e:
        logger.exception(f"Error in video_to_text: {e}")
        raise ValueError("Error processing video data")

