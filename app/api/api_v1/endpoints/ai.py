from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.openai_service import openai_service

router = APIRouter()

class CompletionRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class EmbeddingRequest(BaseModel):
    text: str
    model: Optional[str] = None

class VideoScriptRequest(BaseModel):
    topic: str
    duration: Optional[str] = "60 seconds"
    tone: Optional[str] = "professional and inspiring"
    model: Optional[str] = "gpt-4"

@router.post("/completion", response_model=Dict[str, Any])
async def create_completion(request: CompletionRequest):
    """
    Generate a completion using OpenAI's API
    """
    try:
        response = await openai_service.generate_completion(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embeddings", response_model=List[float])
async def create_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for the given text
    """
    try:
        embeddings = await openai_service.generate_embeddings(
            text=request.text,
            model=request.model
        )
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video-script", response_model=List[Dict[str, Any]])
async def generate_video_script(request: VideoScriptRequest):
    """
    Generate a video script using OpenAI's API
    """
    try:
        script = await openai_service.generate_video_script(
            topic=request.topic,
            duration=request.duration,
            tone=request.tone,
            model=request.model
        )
        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 