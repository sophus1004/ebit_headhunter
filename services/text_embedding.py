import requests
from core.config import AppConfig
from core.messages import ServerMessages
import logging

logger = logging.getLogger("uvicorn.error")

class TextEmbeddings:
    def __init__(self):
        self.config = AppConfig()
        self.embed_url = f"http://{self.config.embedding.host}:{self.config.embedding.port}/embed"

    def get_embeddings(self, texts):
        headers = {"Content-Type": "application/json"}
        data = {
            "inputs": texts,
            "normalize": True,
            "prompt_name": None,
            "truncate": False,
            "truncation_direction": "Right"
        }
        try:
            response = requests.post(self.embed_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            logger.info(ServerMessages.REGISTDATA_CONVERT_COMPLETE)
            return None
        
        return result