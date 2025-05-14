from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.openai_service import openai_service
from app.services.video_generation_service import video_generation_service

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

class VideoScriptRequest(BaseModel):
    product_name: str
    product_description: str
    duration: str = "60 seconds"
    target_audience: str = "general audience"
    language: str = "English"
    brand_name: str = ""
    tone: str = "professional and inspiring"
    ad_type: str = "product showcase"
    variations_no: int = 1

class VideoScriptVariation(BaseModel):
    voiceover_sections: List[Dict[str, Any]]
    stock_footage_keywords: List[str]

class VideoScriptResponse(BaseModel):
    variations: List[VideoScriptVariation]

class VideoGenerationRequest(BaseModel):
    voiceover_sections: List[Dict[str, Any]]
    stock_footage_keywords: List[str]

class VideoGenerationResponse(BaseModel):
    enhanced_script: Dict[str, Any]

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
async def generate_video_script(request: VideoScriptRequest):
    """
    Generate multiple variations of video scripts for a product.
    """
    try:
        variations = await openai_service.generate_video_script(
            product_name=request.product_name,
            product_description=request.product_description,
            duration=request.duration,
            target_audience=request.target_audience,
            language=request.language,
            brand_name=request.brand_name,
            tone=request.tone,
            ad_type=request.ad_type,
            variations_no=request.variations_no
        )
        return VideoScriptResponse(variations=variations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Generate video content from script using Getty Images and Eleven Labs
    """
    try:
        result = await video_generation_service.generate_video_content(request.dict())
        return VideoGenerationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 