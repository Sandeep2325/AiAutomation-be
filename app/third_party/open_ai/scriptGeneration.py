import openai

# Replace with your actual API key
openai.api_key = "YOUR_API_KEY"

def generate_video_script_json(topic: str, duration: str = "60 seconds", tone: str = "professional and inspiring") -> list:
    """
    Generate a structured video script in JSON format using OpenAI.

    Args:
        topic (str): The topic or product the video is about.
        duration (str): Length of the video (e.g., "60 seconds").
        tone (str): Tone of the video (e.g., "professional and inspiring").

    Returns:
        list: A list of scene objects in JSON-like Python dicts.
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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = response['choices'][0]['message']['content'].strip()

        # Try to parse the content safely
        import json
        # Fix triple backticks if any
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        script_json = json.loads(content)
        return script_json

    except Exception as e:
        print("Error generating video script:", e)
        return []
