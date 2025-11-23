import requests
import logging
import base64

logger = logging.getLogger(__name__)

class ElevenLabsService:
    def __init__(self):
        # Replace with your valid ElevenLabs API key
        self.api_key = "sk_f9084572a8747e800a74f59c1f111d735fbab3dfc0d3b720"
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def text_to_speech(self, text, voice_id=None, model_id="eleven_monolingual_v1"):
        """
        Convert text to speech using ElevenLabs API
        """
        if not self.api_key or self.api_key == "YOUR_VALID_ELEVENLABS_API_KEY_HERE":
            raise Exception("Please set a valid ElevenLabs API key")

        voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"

        url = f"{self.base_url}/text-to-speech/{voice_id}"

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        }

        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)

            if response.status_code == 401:
                raise Exception("Invalid API key. Please check your ElevenLabs API key.")
            elif response.status_code == 403:
                raise Exception("API key missing permissions. Upgrade your ElevenLabs plan.")
            elif response.status_code == 429:
                raise Exception("API rate limit exceeded. Please try again later.")

            response.raise_for_status()

            audio_base64 = base64.b64encode(response.content).decode('utf-8')

            return {
                "audio_data": audio_base64,
                "content_type": "audio/mpeg",
                "voice_id": voice_id,
                "text_length": len(text)
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API error: {e}")
            raise Exception(f"Voice generation failed: {str(e)}")

    def get_available_voices(self):
        """Get list of available voices"""
        url = f"{self.base_url}/voices"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 401:
                raise Exception("Invalid API key")
            elif response.status_code == 403:
                raise Exception("API key missing permissions")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching voices: {e}")
            return self.get_default_voices()

    def get_default_voices(self):
        """Return default voices when API is unavailable"""
        return {
            "voices": [
                {
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",
                    "name": "Rachel",
                    "category": "premade",
                    "description": "Female voice - clear and professional"
                },
                {
                    "voice_id": "AZnzlk1XvdvUeBnXmlld",
                    "name": "Domi",
                    "category": "premade",
                    "description": "Female voice - energetic and clear"
                },
                {
                    "voice_id": "EXAVITQu4vr4xnSDxMaL",
                    "name": "Bella",
                    "category": "premade",
                    "description": "Female voice - warm and friendly"
                },
                {
                    "voice_id": "ErXwobaYiN019PkySvjV",
                    "name": "Antoni",
                    "category": "premade",
                    "description": "Male voice - deep and authoritative"
                }
            ]
        }

# Available premium voices
ELEVENLABS_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "domi": "AZnzlk1XvdvUeBnXmlld",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "antoni": "ErXwobaYiN019PkySvjV",
    "elli": "MF3mGyEYCl7XYWbV9V6O",
    "josh": "TxGEqnHWrfWFTfGW9XjX",
    "sam": "yoZ06aMxZJJ28mfd3POQ",
}