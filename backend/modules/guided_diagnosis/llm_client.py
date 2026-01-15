import os
import logging
import requests
import google.generativeai as genai
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed, use system env vars

logger = logging.getLogger(__name__)

class LLMClient:
    def generate(self, prompt: str, system_context: str = ""):
        raise NotImplementedError

class OllamaClient(LLMClient):
    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        logger.info(f"Ollama client initialized: {self.base_url} with model {self.model}")

    def generate(self, prompt: str, system_context: str = ""):
        url = f"{self.base_url}/api/generate"
        
        full_prompt = f"System: {system_context}\n\nUser: {prompt}" if system_context else prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            logger.debug(f"Calling Ollama with model {self.model}")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Error: Request timed out. The model may be loading or overwhelmed."
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            return f"Error contacting Ollama: {str(e)}"

class GeminiClient(LLMClient):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            logger.warning("Gemini API key not configured")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini client initialized")

    def generate(self, prompt: str, system_context: str = ""):
        if not self.api_key:
            return "Error: Gemini API key not configured. Set GEMINI_API_KEY environment variable."
        try:
            full_prompt = f"{system_context}\n\n{prompt}" if system_context else prompt
            logger.debug("Calling Gemini API")
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return f"Error contacting Gemini: {str(e)}"

class LLMFactory:
    @staticmethod
    def get_client(provider: str, config: dict):
        if provider == "ollama":
            return OllamaClient(
                base_url=config.get("url") or os.getenv("OLLAMA_BASE_URL"),
                model=config.get("model") or os.getenv("OLLAMA_MODEL")
            )
        elif provider == "gemini":
            return GeminiClient(api_key=config.get("apiKey") or os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
