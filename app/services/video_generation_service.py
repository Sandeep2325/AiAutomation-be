from typing import Dict, Any, List
import httpx
from app.core.config import settings
import json

class VideoGenerationService:
    def __init__(self):
        self.getty_api_key = settings.GETTY_API_KEY
        self.eleven_labs_api_key = settings.ELEVEN_LABS_API_KEY
        self.getty_base_url = "https://api.gettyimages.com/v3/search/images"
        self.eleven_labs_base_url = "https://api.elevenlabs.io/v1/text-to-speech"

    async def get_stock_footage(self, query: str) -> Dict[str, Any]:
        """
        Search for stock footage using Getty Images API
        """
        if not self.getty_api_key:
            return {
                "id": "demo",
                "title": "Demo Footage",
                "preview_url": "https://d25u9hypq51glx.cloudfront.net/arole/3cb7e03d-a95c-4102-86b8-20c5bc8630ed/video/d0b41e2b-76a0-4be6-8bfa-1115b3707f9f/video.mp4",
                "download_url": "https://d25u9hypq51glx.cloudfront.net/arole/3cb7e03d-a95c-4102-86b8-20c5bc8630ed/video/d0b41e2b-76a0-4be6-8bfa-1115b3707f9f/video.mp4",
                "note": "Getty Images API key not configured"
            }

        headers = {
            "Api-Key": self.getty_api_key,
            "Accept": "application/json"
        }
        params = {
            "phrase": query,
            "fields": "id,title,display_sizes,preview",
            "sort_order": "best_match",
            "page_size": 1
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.getty_base_url,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("images"):
                image = data["images"][0]
                return {
                    "id": image["id"],
                    "title": image["title"],
                    "preview_url": image["display_sizes"][0]["uri"],
                    "download_url": image["display_sizes"][-1]["uri"]
                }
            return None

    async def generate_voiceover(self, text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Dict[str, Any]:
        """
        Generate voiceover using Eleven Labs API
        """
        if not self.eleven_labs_api_key:
            return {
                "url": "https://d25u9hypq51glx.cloudfront.net/audio_projects/whisper/3cb7e03d-a95c-4102-86b8-20c5bc8630ed/848380575464/audio.mp3",
                "text": text,
                "note": "Eleven Labs API key not configured"
            }

        headers = {
            "xi-api-key": self.eleven_labs_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.eleven_labs_base_url}/{voice_id}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            # Save the audio file and return the URL
            # In a production environment, you'd want to save this to a cloud storage service
            audio_url = f"/audio/{voice_id}_{hash(text)}.mp3"
            return {
                "url": audio_url,
                "text": text
            }

    async def generate_video_content(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video content from script using Getty Images and Eleven Labs
        """
        try:
            enhanced_sections = []
            
            for section in script["voiceover_sections"]:
                # Generate voiceover
                voiceover = await self.generate_voiceover(section["voiceover"])
                background_music = {
                    "url": "https://d25u9hypq51glx.cloudfront.net/image_projects/3cb7e03d-a95c-4102-86b8-20c5bc8630ed/assets/audio/13592a75-3fa1-42f8-8b21-cc72b3bd54ef/audio.mp3",
                    "text": "Background Music",
                    "note": "Eleven Labs API key not configured"
                }
                # Get footage for each scene
                enhanced_scenes = []
                for scene in section["scenes"]:
                    # Try each search query until we find a match
                    footage = None
                    for query in scene["search_queries"]:
                        footage = await self.get_stock_footage(query)
                        if footage:
                            break
                    
                    enhanced_scenes.append({
                        **scene,
                        "footage": footage
                    })
                
                enhanced_sections.append({
                    "voiceover": voiceover,
                    "scenes": enhanced_scenes
                })

                enhanced_sections.append({
                    "background_music": background_music
                })
            
            return {
                "enhanced_script": {
                    "voiceover_sections": enhanced_sections,
                    "stock_footage_keywords": script["stock_footage_keywords"]
                }
            }
            
        except Exception as e:
            raise Exception(f"Error generating video content: {str(e)}")

video_generation_service = VideoGenerationService() 