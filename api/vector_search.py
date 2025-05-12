import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymilvus import connections, Collection
from typing import Any
from services.text_embedding import TextEmbeddings
from core.messages import ServerMessages

logger = logging.getLogger("uvicorn.error")


class VectorSearch:
    """텍스트 쿼리에 대한 벡터 임베딩 기반의 Milvus 검색 및 연동된 MariaDB 결과 조회를 수행하는 클래스입니다.

    Attributes:
        text_embedding (TextEmbeddings): 텍스트 임베딩 생성기.
        initialize_db (InitializeDB): DB 엔진 접근을 위한 초기화 객체.
        config (AppConfig): 앱 전역 설정 객체.
        mariadb_config (MariaDBConfig): MariaDB 설정 객체.
        milvus_config (MilvusConfig): Milvus 설정 객체.
        embedding_config (EmbeddingConfig): 임베딩 서버 설정 객체.
        data_config (DataConfig): 데이터 스키마 및 컬렉션 설정 객체.
    """

    def __init__(self, config, initialize_db):
        """VectorSearch 클래스 초기화 메서드.

        Args:
            config (AppConfig): 설정 객체.
            initialize_db (InitializeDB): DB 연결 및 엔진 접근용 객체.
        """
        self.text_embedding = TextEmbeddings()

        self.initialize_db = initialize_db

        self.config = config
        self.mariadb_config = config.mariadb
        self.milvus_config = config.milvus
        self.embedding_config = config.embedding
        self.data_config = config.data

    def _milvus_search(self, col: str, metric_type: str, nprobe: int, embedded_data: list, top_k: int, output_fields: list):
        """Milvus에서 벡터 유사도 검색을 수행합니다.

        Args:
            col (str): 검색할 컬렉션 이름.
            metric_type (str): 유사도 측정 방식 (예: "COSINE").
            nprobe (int): 검색 정확도 조절을 위한 nprobe 값.
            embedded_data (list): 쿼리 임베딩 벡터 리스트.
            top_k (int): 반환할 유사 결과 수.
            output_fields (list): 반환할 필드 목록.

        Returns:
            list: Milvus 검색 결과.
        """
        try:
            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": nprobe}
            }

            collection = Collection(col)
            results = collection.search(
                data=embedded_data,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=output_fields
            )

            return results

        except Exception as e:
            logger.error(ServerMessages.MILVUS_SEARCH_ERROR + f"{e}")

    def _mariadb_search(self, id_list: list):
        """Milvus 검색 결과로 얻은 ID를 통해 MariaDB에서 상세 데이터를 조회합니다.

        Args:
            id_list (list): Milvus 검색 결과에서 추출한 ID 리스트.

        Returns:
            list[dict]: 조회된 MariaDB 레코드 목록.
        """
        try:
            with self.initialize_db.engine.connect() as conn:
                placeholders = ", ".join([":id{}".format(i) for i in range(len(id_list))])
                sql = text(f"SELECT * FROM {self.mariadb_config.table} WHERE id IN ({placeholders})")
                params = {f"id{i}": id_val for i, id_val in enumerate(id_list)}

                result = conn.execute(sql, params)
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(ServerMessages.MARIA_SEARCH_ERROR + f"{e}")

    def only_vector(self, collection_names: str, query_text: str, top_k: int):
        """텍스트 쿼리를 임베딩하여 Milvus에서 유사 문서 검색 후 MariaDB에서 상세 정보 반환.

        Args:
            collection_names (str): 검색 대상 컬렉션 이름.
            query_text (str): 사용자가 입력한 검색 쿼리.
            top_k (int): 검색 결과 개수.

        Returns:
            list[dict]: 유사도 기반 검색 결과 상세 정보 리스트.
        """
        col = collection_names
        metric_type = "COSINE"
        nprobe = 10
        embedded_data = self.text_embedding.get_embeddings([query_text])
        output_fields = ["id"]

        milvus_result = self._milvus_search(col, metric_type, nprobe, embedded_data, top_k, output_fields)
        id_list = [hit.id for hit in milvus_result[0]]
        mariadb_result = self._mariadb_search(id_list)

        return mariadb_result