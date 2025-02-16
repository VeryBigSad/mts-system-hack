from io import BytesIO
import logging

from fastapi import APIRouter, status

from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ping"])


class RequestData(BaseModel):
    text: str


@router.post("", status_code=status.HTTP_200_OK)
async def text_to_speech(data: RequestData) -> StreamingResponse:
    """Ping us!"""
    audio_bytes = text_to_speech(data.text)
    return StreamingResponse(audio_bytes, media_type="audio/mp3")


def text_to_speech(text: str) -> BytesIO:
    """
    Конвертация текста в речь с использованием Google Text-to-Speech
    
    Args:
        text: Текст для преобразования
        
    Returns:
        str: Путь к созданному аудио файлу или пустая строка в случае ошибки
    """
    try:
        # Создаем объект gTTS
        tts = gTTS(text=text, lang='ru', slow=False)
        # save audio to bytes object
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes

    except Exception as e:
        print(f"Ошибка при конвертации текста в речь: {str(e)}")
        return ""

if __name__ == "__main__":

    text = "Привет, это тестовое сообщение через Google Text-to-Speech"
    result = text_to_speech(text, "output.mp3")
    if result:
        print(f"Аудио сохранено в: {result}")