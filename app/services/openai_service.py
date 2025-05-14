from openai import AsyncOpenAI
from app.core.config import settings
from typing import Optional, List, Dict, Any
import json

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE

    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using OpenAI's API
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens
        )

        return {
            "content": response.choices[0].message.content,
            "usage": response.usage.dict(),
            "model": response.model
        }

    async def generate_embeddings(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """
        Generate embeddings for the given text
        """
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding

    async def generate_video_script(
        self,
        product_name: str,
        product_description: str,
        duration: str = "60 seconds",
        target_audience: str = "general audience",
        language: str = "English",
        brand_name: str = "",
        tone: str = "professional and inspiring",
        ad_type: str = "product showcase",
        variations_no: int = 1,
        model: Optional[str] = "gpt-4.1-nano"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple variations of structured video scripts in JSON format using OpenAI.
        """
        script_prompt = f"""
You're a professional video scriptwriter specializing in product marketing.

Generate a complete video script in JSON format for a {duration} {ad_type} promotional video about {product_name}.
Product Description: {product_description}
Target Audience: {target_audience}
Language: {language}
Brand Name: {brand_name}
Tone: {tone}
Ad Type: {ad_type}

The script should be organized into voiceover sections, where each section can have multiple scenes.
Each voiceover section should include:
- voiceover (the narration text)
- scenes (array of scenes that play during this voiceover)

Each scene should include:
- scene_number (sequential number across all scenes)
- visual (visual description of the scene)
- caption (on-screen text in {language})
- music_sfx (background music or sound effects)
- search_queries (array of 3-5 specific search queries for finding stock footage for this scene)

Guidelines for scenes:
1. Each voiceover section can have 1-3 scenes
2. Scenes should flow naturally with the voiceover
3. Use visual transitions between scenes
4. Consider timing and pacing
5. Ensure scenes support the voiceover message

Guidelines for search_queries:
1. Each query should be specific to the scene's visual needs
2. Include both broad and specific terms
3. Consider camera angles and movements
4. Include relevant props or elements
5. Consider lighting and atmosphere
6. Use terms commonly found in stock footage websites

Example structure:
{{
    "voiceover_sections": [
        {{
            "voiceover": "Welcome to the future of home living",
            "scenes": [
                {{
                    "scene_number": 1,
                    "visual": "Wide shot of modern home exterior",
                    "caption": "SmartHome Hub",
                    "music_sfx": "Modern, tech-inspired background music",
                    "search_queries": ["modern home exterior", "contemporary architecture", "smart home"]
                }},
                {{
                    "scene_number": 2,
                    "visual": "Close-up of smart door lock",
                    "caption": "Secure & Connected",
                    "music_sfx": "Continuing background music",
                    "search_queries": ["smart door lock", "security technology", "home automation"]
                }}
            ]
        }}
    ]
}}

Return the result as a valid JSON object with voiceover_sections array.
Ensure the output is directly parseable JSON.
        """

        keywords_prompt = f"""
Based on the following product information, generate at least 4 relevant keywords for stock footage selection:

Product: {product_name}
Description: {product_description}
Target Audience: {target_audience}
Tone: {tone}

The keywords should be:
1. Specific and relevant to the product
2. Useful for finding stock footage
3. Include both product-specific and emotional/atmospheric terms
4. Be in {language}

Return the keywords as a JSON array of strings.
        """

        try:
            # Generate multiple variations concurrently
            script_tasks = []
            for i in range(variations_no):
                # Add variation number to prompt for diversity
                variation_prompt = f"{script_prompt}\n\nThis is variation {i+1} of {variations_no}. Please ensure this variation is unique and different from other variations."
                script_tasks.append(
                    self.client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": variation_prompt}],
                        temperature=0.7 + (i * 0.1)  # Increase temperature for each variation
                    )
                )

            # Generate keywords once as they can be shared across variations
            keywords_response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": keywords_prompt}],
                temperature=0.7
            )
            keywords_content = keywords_response.choices[0].message.content.strip()

            # Parse keywords
            if keywords_content.startswith("```json"):
                keywords_content = keywords_content.split("```json")[1].split("```")[0].strip()
            elif keywords_content.startswith("```"):
                keywords_content = keywords_content.split("```")[1].split("```")[0].strip()
            keywords = json.loads(keywords_content)

            # Process all script variations
            results = []
            for script_task in script_tasks:
                script_response = await script_task
                script_content = script_response.choices[0].message.content.strip()

                # Parse script
                if script_content.startswith("```json"):
                    script_content = script_content.split("```json")[1].split("```")[0].strip()
                elif script_content.startswith("```"):
                    script_content = script_content.split("```")[1].split("```")[0].strip()
                script_data = json.loads(script_content)

                results.append({
                    "voiceover_sections": script_data["voiceover_sections"],
                    "stock_footage_keywords": keywords
                })

            return results

        except Exception as e:
            raise Exception(f"Error generating video scripts: {str(e)}")

openai_service = OpenAIService() 