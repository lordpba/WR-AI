import requests
import google.generativeai as genai
import os

class LLMClient:
    def generate(self, prompt: str, system_context: str = ""):
        raise NotImplementedError

class OllamaClient(LLMClient):
    def __init__(self, base_url="http://localhost:11434", model="llama3.1:latest"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, system_context: str = ""):
        url = f"{self.base_url}/api/generate"
        
        full_prompt = f"System: {system_context}\n\nUser: {prompt}" if system_context else prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error contacting Ollama: {str(e)}"

class GeminiClient(LLMClient):
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate(self, prompt: str, system_context: str = ""):
        try:
            # Gemini supports system instructions in newer versions, but simpler to prepend for compatibility
            full_prompt = f"{system_context}\n\n{prompt}" if system_context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error contacting Gemini: {str(e)}"

class LLMFactory:
    @staticmethod
    def get_client(provider: str, config: dict):
        if provider == "ollama":
            return OllamaClient(
                base_url=config.get("url", "http://localhost:11434"),
                model=config.get("model", "llama3.1:latest")
            )
        elif provider == "gemini":
            return GeminiClient(api_key=config.get("apiKey", ""))
        else:
            raise ValueError("Unknown provider")
