import requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from typing import Any

class VectorSearch:
    def __init__(self, config):
        self.config = config

        # MariaDB 연결
        mariadb = config.mariadb
        DATABASE_URL = (
            f"mysql+pymysql://{mariadb.user}:{mariadb.password}"
            f"@{mariadb.host}:{mariadb.port}/{mariadb.database}"
        )
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)

        # Milvus 연결
        if not connections.has_connection("default"):
            connections.connect(
                alias="default",
                host=config.milvus.host,
                port=int(config.milvus.port)
            )

    def get_embedding(self, text: str) -> list[float] | None:
        url = "http://host.docker.internal:3201/embed"
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": [text],
            "normalize": True,
            "prompt_name": None,
            "truncate": False,
            "truncation_direction": "Right"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()[0]
        except Exception as e:
            print(f"[Embedding Error] {e}")
            return None

    def fetch_from_mariadb(self, id_value: Any) -> dict | None:
        try:
            session = self.Session()
            query = text("SELECT * FROM person_info WHERE id = :id")
            result = session.execute(query, {"id": id_value}).fetchone()
            session.close()
            if result:
                return dict(result._mapping)
            return None
        except Exception as e:
            print(f"[MariaDB Error] {e}")
            return None

    def search(self, collection_names: list[str], query_text: str, top_k: int = 1) -> list[dict]:
        embedding = self.get_embedding(query_text)
        if not embedding:
            return [{"error": "embedding 생성 실패"}]

        all_results = []

        for collection_name in collection_names:
            try:
                collection = Collection(collection_name)
                collection.load()

                search_params = {
                    "metric_type": "COSINE",
                    "params": {"nprobe": 10}
                }

                results = collection.search(
                    data=[embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=["id", "text"]
                )

                for hit in results[0]:
                    milvus_id = hit.entity.get("id")
                    record = self.fetch_from_mariadb(milvus_id)
                    all_results.append({
                        "collection": collection_name,
                        "id": milvus_id,
                        "score": round(hit.distance, 4),
                        "text": hit.entity.get("text"),
                        "record": record
                    })
            except Exception as e:
                all_results.append({"collection": collection_name, "error": str(e)})

        return all_results