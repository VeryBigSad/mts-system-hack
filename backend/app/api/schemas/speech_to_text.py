from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str


class ProcessingResponse(BaseModel):
    request_id: str
    status: str


class TranscriptionResult(BaseModel):
    text: str
    request_id: str
