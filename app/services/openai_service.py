from openai import OpenAI
from app.core.config import settings
from typing import Optional, List, Dict, Any
import json

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
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
        topic: str,
        duration: str = "60 seconds",
        tone: str = "professional and inspiring",
        model: str = "gpt-4"
    ) -> List[Dict[str, Any]]:
        """
        Generate a structured video script in JSON format using OpenAI.
        """
        prompt = f"""
You're a professional video scriptwriter.

Generate a complete video script in JSON format for a {duration} promotional video about {topic}.
The tone should be {tone}.

Each scene should include the following fields:
- scene (number)
- visual (visual description of the scene)
- narration (voiceover line)
- caption (on-screen text)
- music_sfx (background music or sound effects)

Return the result as a valid JSON array of scene objects.
Ensure the output is directly parseable JSON.
        """

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()

            # Fix triple backticks if any
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            script_json = json.loads(content)
            return script_json

        except Exception as e:
            raise Exception(f"Error generating video script: {str(e)}")

openai_service = OpenAIService() 