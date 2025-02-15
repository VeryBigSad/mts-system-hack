from pydantic import BaseModel

from app.api.schemas.ai import AIResponse


class TextRequest(BaseModel):
    text: str

class ProcessingResponse(BaseModel):
    response: AIResponse

class TranscriptionResult(BaseModel):
    text: str
    request_id: str
