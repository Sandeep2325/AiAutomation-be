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

class Scene(BaseModel):
    scene_number: int
    visual: str
    caption: str
    music_sfx: str
    search_queries: List[str]

class VoiceoverSection(BaseModel):
    voiceover: str
    scenes: List[Scene]

class VideoScriptResponse(BaseModel):
    voiceover_sections: List[VoiceoverSection]
    stock_footage_keywords: List[str]

class VideoScriptRequest(BaseModel):
    product_name: str
    product_description: str
    duration: str = "60 seconds"
    target_audience: str
    language: str = "English"
    brand_name: str
    tone: Optional[str] = "professional and inspiring"
    model: Optional[str] = "gpt-4.1-nano"

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

@router.post("/video-script", response_model=VideoScriptResponse)
def generate_video_script(request: VideoScriptRequest):
    """
    Generate a video script using OpenAI's API
    """
    try:
        script = openai_service.generate_video_script(
            product_name=request.product_name,
            product_description=request.product_description,
            duration=request.duration,
            target_audience=request.target_audience,
            language=request.language,
            brand_name=request.brand_name,
            tone=request.tone,
            model=request.model
        )
        return script
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 