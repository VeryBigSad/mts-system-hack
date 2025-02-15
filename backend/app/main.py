from fastapi import FastAPI
from app.api.routes.v1.ai import router as speech_router

app = FastAPI(title="MTS Hackathon API", description="API for speech and text processing", version="1.0.0")

app.include_router(speech_router, prefix="/v1")
