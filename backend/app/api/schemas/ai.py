from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    status: str = Field(..., description="The status of the response")
    task: str = Field(..., description="The task that the AI chose")
    parameters: dict = Field(..., description="The parameters for the task")
    reasoning: str = Field(..., description="The reasoning for the task")


class GigaChatResponse(BaseModel):
    text: str

