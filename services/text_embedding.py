import requests
from core.config import AppConfig
from core.messages import ServerMessages
import logging

logger = logging.getLogger("uvicorn.error")


class TextEmbeddings:
    """텍스트 임베딩 벡터를 생성하는 클래스입니다.

    외부 임베딩 서버와 통신하여 주어진 텍스트 리스트에 대한 벡터를 반환합니다.

    Attributes:
        config (AppConfig): 애플리케이션 설정을 담고 있는 객체.
        embed_url (str): 임베딩 요청을 보낼 API의 엔드포인트 URL.
    """

    def __init__(self):
        """TextEmbeddings 클래스의 인스턴스를 초기화합니다.

        AppConfig를 로드하고, 임베딩 서버의 URL을 구성합니다.
        """
        self.config = AppConfig()
        self.embed_url = f"http://{self.config.embedding.host}:{self.config.embedding.port}/embed"

    def get_embeddings(self, texts):
        """입력된 텍스트 리스트에 대해 임베딩 벡터를 요청합니다.

        Args:
            texts (List[str]): 임베딩을 생성할 텍스트 리스트.

        Returns:
            dict or None: 정상적으로 처리되면 임베딩 결과를 포함한 JSON 딕셔너리,
                          실패 시 None을 반환합니다.
        """
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
            logger.error(ServerMessages.EMBEDDING_ERROR)
            return None

        return result